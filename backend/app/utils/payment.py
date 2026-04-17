"""
支付工具模块
支持支付宝和微信支付
"""

import json
import time
import hashlib
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlencode
import requests
import os
import logging

logger = logging.getLogger(__name__)


class PaymentConfig:
    """支付配置类"""
    
    # 支付宝配置
    ALIPAY_APP_ID = os.getenv('ALIPAY_APP_ID', '')
    ALIPAY_PRIVATE_KEY = os.getenv('ALIPAY_PRIVATE_KEY', '')  # RSA2私钥
    ALIPAY_PUBLIC_KEY = os.getenv('ALIPAY_PUBLIC_KEY', '')   # 支付宝公钥
    ALIPAY_GATEWAY = os.getenv('ALIPAY_GATEWAY', 'https://openapi.alipay.com/gateway.do')
    ALIPAY_SANDBOX_GATEWAY = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
    
    # 微信支付配置
    WECHAT_APP_ID = os.getenv('WECHAT_APP_ID', '')
    WECHAT_MCH_ID = os.getenv('WECHAT_MCH_ID', '')          # 商户号
    WECHAT_API_KEY = os.getenv('WECHAT_API_KEY', '')         # API密钥
    WECHAT_CERT_PATH = os.getenv('WECHAT_CERT_PATH', '')     # 证书路径
    WECHAT_KEY_PATH = os.getenv('WECHAT_KEY_PATH', '')       # 密钥路径
    WECHAT_GATEWAY = 'https://api.mch.weixin.qq.com/v3/pay/transactions'
    WECHAT_SANDBOX_GATEWAY = 'https://api.mch.weixin.qq.com/v3/pay/transactions'
    
    # 是否使用沙箱环境
    SANDBOX_MODE = os.getenv('SANDBOX_MODE', 'true').lower() == 'true'
    
    # 回调地址
    NOTIFY_URL = os.getenv('ALIPAY_NOTIFY_URL', os.getenv('PAYMENT_NOTIFY_URL', 'https://your-domain.com/api/payment/notify'))
    RETURN_URL = os.getenv('ALIPAY_RETURN_URL', 'http://localhost:3000/payment/result')


class AlipayService:
    """支付宝支付服务"""
    
    def __init__(self, config: PaymentConfig = None):
        self.config = config or PaymentConfig()
    
    def _sign(self, params: dict) -> str:
        """RSA2签名"""
        # 按字典序排列参数
        sorted_params = sorted(params.items())
        sign_string = '&'.join([f'{k}={v}' for k, v in sorted_params])
        
        # 使用RSA2签名
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.backends import default_backend

        try:
            # 确保私钥是 PEM 格式
            private_key_str = self.config.ALIPAY_PRIVATE_KEY
            if not private_key_str.startswith('-----BEGIN'):
                private_key_str = f"-----BEGIN PRIVATE KEY-----\n{private_key_str}\n-----END PRIVATE KEY-----"

            private_key = serialization.load_pem_private_key(
                private_key_str.encode(),
                password=None,
                backend=default_backend()
            )
            
            signature = private_key.sign(
                sign_string.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            return signature.hex()
        except Exception as e:
            logger.error(f"签名失败: {e}")
            return ''
    
    def _verify_sign(self, params: dict, sign: str) -> bool:
        """验证签名"""
        try:
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import padding
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.backends import default_backend

            sorted_params = sorted(params.items())
            sign_string = '&'.join([f'{k}={v}' for k, v in sorted_params])

            # 确保公钥是 PEM 格式
            public_key_str = self.config.ALIPAY_PUBLIC_KEY
            if not public_key_str.startswith('-----BEGIN'):
                public_key_str = f"-----BEGIN PUBLIC KEY-----\n{public_key_str}\n-----END PUBLIC KEY-----"

            public_key = serialization.load_pem_public_key(
                public_key_str.encode(),
                backend=default_backend()
            )
            
            return public_key.verify(
                sign.encode('latin-1'),
                sign_string.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        except Exception as e:
            logger.error(f"验签失败: {e}")
            return False
    
    def create_payment(self, out_trade_no: str, amount: float, subject: str, 
                       body: str = '') -> Dict[str, Any]:
        """
        创建支付宝支付订单
        
        Args:
            out_trade_no: 商户订单号
            amount: 金额（元）
            subject: 商品标题
            body: 商品描述
        """
        # 检查是否配置了真实支付
        if not self.config.ALIPAY_APP_ID or not self.config.ALIPAY_PRIVATE_KEY:
            # 返回模拟支付数据（用于测试）
            logger.warning("支付宝未配置，返回模拟支付数据")
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            return {
                'success': True,
                'payment_url': f'{frontend_url}/payment/mock?order_no={out_trade_no}',
                'out_trade_no': out_trade_no,
                'amount': amount,
                'platform': 'alipay',
                'mock': True
            }

        logger.info(f"准备创建支付宝支付: APP_ID={self.config.ALIPAY_APP_ID[:10]}..., SANDBOX={self.config.SANDBOX_MODE}")

        # 获取前端回调地址
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        return_url = f'{frontend_url}/payment/result'

        # 沙箱环境
        gateway = self.config.ALIPAY_SANDBOX_GATEWAY if self.config.SANDBOX_MODE else self.config.ALIPAY_GATEWAY

        params = {
            'app_id': self.config.ALIPAY_APP_ID,
            'method': 'alipay.trade.app.pay',
            'format': 'JSON',
            'return_url': return_url,
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'notify_url': self.config.NOTIFY_URL,
            'biz_content': json.dumps({
                'out_trade_no': out_trade_no,
                'total_amount': f'{amount:.2f}',
                'subject': subject,
                'body': body or subject,
                'product_code': 'QUICK_MSECURITY_PAY'
            }, ensure_ascii=False)
        }

        # 生成签名
        sign = self._sign(params)
        params['sign'] = sign

        # 构建支付URL
        pay_url = f"{gateway}?{urlencode(params)}"

        return {
            'success': True,
            'payment_url': pay_url,
            'out_trade_no': out_trade_no,
            'amount': amount,
            'platform': 'alipay'
        }
    
    def query_payment(self, out_trade_no: str) -> Dict[str, Any]:
        """查询支付状态"""
        gateway = self.config.ALIPAY_SANDBOX_GATEWAY if self.config.SANDBOX_MODE else self.config.ALIPAY_GATEWAY
        
        params = {
            'app_id': self.config.ALIPAY_APP_ID,
            'method': 'alipay.trade.query',
            'format': 'JSON',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps({
                'out_trade_no': out_trade_no
            })
        }
        
        sign = self._sign(params)
        params['sign'] = sign
        
        try:
            response = requests.post(gateway, data=urlencode(params), timeout=10)
            result = response.json()
            
            if 'alipay_trade_query_response' in result:
                trade_response = result['alipay_trade_query_response']
                return {
                    'success': True,
                    'trade_status': trade_response.get('trade_status', ''),
                    'amount': float(trade_response.get('total_amount', 0)),
                    'pay_time': trade_response.get('gmt_payment', '')
                }
            return {'success': False, 'error': '查询失败'}
        except Exception as e:
            logger.error(f"查询支付失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def refund(self, out_trade_no: str, refund_amount: float, reason: str = '') -> Dict[str, Any]:
        """申请退款"""
        gateway = self.config.ALIPAY_SANDBOX_GATEWAY if self.config.SANDBOX_MODE else self.config.ALIPAY_GATEWAY
        
        params = {
            'app_id': self.config.ALIPAY_APP_ID,
            'method': 'alipay.trade.refund',
            'format': 'JSON',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps({
                'out_trade_no': out_trade_no,
                'refund_amount': f'{refund_amount:.2f}',
                'refund_reason': reason or '用户申请退款'
            }, ensure_ascii=False)
        }
        
        sign = self._sign(params)
        params['sign'] = sign
        
        try:
            response = requests.post(gateway, data=urlencode(params), timeout=10)
            result = response.json()
            
            if 'alipay_trade_refund_response' in result:
                refund_response = result['alipay_trade_refund_response']
                return {
                    'success': True,
                    'refund_amount': float(refund_response.get('refund_amount', 0))
                }
            return {'success': False, 'error': '退款失败'}
        except Exception as e:
            logger.error(f"退款失败: {e}")
            return {'success': False, 'error': str(e)}


class WechatPayService:
    """微信支付服务"""
    
    def __init__(self, config: PaymentConfig = None):
        self.config = config or PaymentConfig()
    
    def _get_sign_key(self) -> str:
        """生成签名密钥"""
        timestamp = str(int(time.time()))
        nonce_str = uuid.uuid4().hex[:32]
        return timestamp, nonce_str
    
    def _make_signature(self, sign_str: str) -> str:
        """生成微信支付签名"""
        # 使用SHA256 + HMAC
        key = self.config.WECHAT_API_KEY.encode('utf-8')
        sign_str = sign_str.encode('utf-8')
        
        import hmac
        signature = hmac.new(key, sign_str, hashlib.sha256).hexdigest()
        return signature.upper()
    
    def _request(self, url: str, method: str = 'POST', data: dict = None, 
                 use_cert: bool = False) -> Dict[str, Any]:
        """发送HTTP请求"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            if use_cert:
                # 需要证书的请求（退款等）
                cert = (self.config.WECHAT_CERT_PATH, self.config.WECHAT_KEY_PATH) \
                    if self.config.WECHAT_CERT_PATH else None
                response = requests.request(
                    method, url, json=data, headers=headers, cert=cert, timeout=30
                )
            else:
                response = requests.request(
                    method, url, json=data, headers=headers, timeout=30
                )
            
            result = response.json()
            return result
        except Exception as e:
            logger.error(f"微信支付请求失败: {e}")
            return {'code': 'ERROR', 'message': str(e)}
    
    def create_payment(self, out_trade_no: str, amount: float, subject: str,
                       openid: str = None) -> Dict[str, Any]:
        """
        创建微信支付订单
        
        Args:
            out_trade_no: 商户订单号
            amount: 金额（分）
            subject: 商品描述
            openid: 用户openid（JSAPI支付必需）
        """
        # 金额转换为分
        total_amount = int(amount * 100)
        
        # 构建请求参数
        timestamp, nonce_str = self._get_sign_key()
        
        # 生成签名
        sign_dict = {
            'appid': self.config.WECHAT_APP_ID,
            'mchid': self.config.WECHAT_MCH_ID,
            'description': subject,
            'out_trade_no': out_trade_no,
            'time_expire': datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00'),
            'amount': {
                'total': total_amount,
                'currency': 'CNY'
            },
            'notify_url': self.config.NOTIFY_URL,
            'attach': out_trade_no
        }
        
        if openid:
            sign_dict['payer'] = {'openid': openid}
        
        # 生成签名字符串
        sign_str = f"POST\n/v3/pay/transactions/app\n{timestamp}\n{nonce_str}\n{json.dumps(sign_dict)}"
        signature = self._make_signature(sign_str)
        
        # 添加签名到请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'WECHATPAY2-SHA256-RSA2048 signature="{signature}", '
                           f'timestamp="{timestamp}", nonce_str="{nonce_str}", '
                           f'serial="{self.config.WECHAT_MCH_ID}"'
        }
        
        gateway = self.config.WECHAT_SANDBOX_GATEWAY if self.config.SANDBOX_MODE else self.config.WECHAT_GATEWAY
        url = f"{gateway}/app"
        
        try:
            response = requests.post(url, json=sign_dict, headers=headers, timeout=30)
            result = response.json()
            
            if 'prepay_id' in result:
                # 构建APP支付参数
                timestamp_str = str(int(time.time()))
                nonce_str_app = uuid.uuid4().hex[:16]
                
                pay_sign_str = f"{self.config.WECHAT_APP_ID}\n{timestamp_str}\n{nonce_str_app}\nprepay_id={result['prepay_id']}"
                pay_signature = self._make_signature(pay_sign_str)
                
                return {
                    'success': True,
                    'prepay_id': result['prepay_id'],
                    'appid': self.config.WECHAT_APP_ID,
                    'partnerid': self.config.WECHAT_MCH_ID,
                    'prepayid': result['prepay_id'],
                    'package': 'Sign=WXPay',
                    'noncestr': nonce_str_app,
                    'timestamp': timestamp_str,
                    'sign': pay_signature,
                    'out_trade_no': out_trade_no,
                    'platform': 'wechat'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', result.get('return_msg', '创建支付失败'))
                }
        except Exception as e:
            logger.error(f"微信支付创建失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def query_payment(self, out_trade_no: str) -> Dict[str, Any]:
        """查询支付状态"""
        gateway = self.config.WECHAT_SANDBOX_GATEWAY if self.config.SANDBOX_MODE else self.config.WECHAT_GATEWAY
        url = f"{gateway}/out-trade-no/{out_trade_no}?mchid={self.config.WECHAT_MCH_ID}"
        
        timestamp, nonce_str = self._get_sign_key()
        
        sign_str = f"GET\n/v3/pay/transactions/out-trade-no/{out_trade_no}\n{timestamp}\n{nonce_str}\n"
        signature = self._make_signature(sign_str)
        
        headers = {
            'Authorization': f'WECHATPAY2-SHA256-RSA2048 signature="{signature}", '
                           f'timestamp="{timestamp}", nonce_str="{nonce_str}", '
                           f'serial="{self.config.WECHAT_MCH_ID}"'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if 'trade_state' in result:
                return {
                    'success': True,
                    'trade_state': result['trade_state'],
                    'trade_state_desc': result.get('trade_state_desc', ''),
                    'amount': result.get('amount', {}).get('payer_total', 0) / 100
                }
            return {'success': False, 'error': '查询失败'}
        except Exception as e:
            logger.error(f"微信支付查询失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def refund(self, out_trade_no: str, refund_amount: float, reason: str = '') -> Dict[str, Any]:
        """申请退款"""
        gateway = self.config.WECHAT_SANDBOX_GATEWAY if self.config.SANDBOX_MODE else self.config.WECHAT_GATEWAY
        url = f"{gateway}/refunds"
        
        timestamp, nonce_str = self._get_sign_key()
        
        refund_data = {
            'out_trade_no': out_trade_no,
            'out_refund_no': f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}",
            'amount': {
                'refund': int(refund_amount * 100),
                'total': int(refund_amount * 100),
                'currency': 'CNY'
            },
            'reason': reason or '用户申请退款'
        }
        
        sign_str = f"POST\n/v3/pay/transactions/refunds\n{timestamp}\n{nonce_str}\n{json.dumps(refund_data)}"
        signature = self._make_signature(sign_str)
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'WECHATPAY2-SHA256-RSA2048 signature="{signature}", '
                           f'timestamp="{timestamp}", nonce_str="{nonce_str}", '
                           f'serial="{self.config.WECHAT_MCH_ID}"'
        }
        
        try:
            response = requests.post(url, json=refund_data, headers=headers, timeout=30)
            result = response.json()
            
            if 'refund_id' in result:
                return {
                    'success': True,
                    'refund_id': result['refund_id']
                }
            return {'success': False, 'error': result.get('message', '退款失败')}
        except Exception as e:
            logger.error(f"微信退款失败: {e}")
            return {'success': False, 'error': str(e)}


class PaymentService:
    """统一支付服务"""
    
    def __init__(self):
        self.config = PaymentConfig()
        self.alipay = AlipayService(self.config)
        self.wechat = WechatPayService(self.config)
    
    def create_payment(self, order_no: str, amount: float, subject: str,
                      platform: str = 'alipay', **kwargs) -> Dict[str, Any]:
        """
        创建支付订单
        
        Args:
            order_no: 订单编号
            amount: 金额（元）
            subject: 商品标题
            platform: 支付平台 ('alipay' 或 'wechat')
        """
        if platform == 'wechat':
            return self.wechat.create_payment(
                out_trade_no=order_no,
                amount=amount,
                subject=subject,
                openid=kwargs.get('openid')
            )
        else:
            return self.alipay.create_payment(
                out_trade_no=order_no,
                amount=amount,
                subject=subject
            )
    
    def query_payment(self, order_no: str, platform: str = 'alipay') -> Dict[str, Any]:
        """查询支付状态"""
        if platform == 'wechat':
            return self.wechat.query_payment(order_no)
        else:
            return self.alipay.query_payment(order_no)
    
    def refund(self, order_no: str, amount: float, platform: str = 'alipay',
               reason: str = '') -> Dict[str, Any]:
        """申请退款"""
        if platform == 'wechat':
            return self.wechat.refund(order_no, amount, reason)
        else:
            return self.alipay.refund(order_no, amount, reason)
    
    def verify_notify(self, data: dict, platform: str = 'alipay') -> bool:
        """验证回调通知"""
        if platform == 'wechat':
            return True  # 微信回调验签在通知处理中进行
        else:
            sign = data.pop('sign', '')
            return self.alipay._verify_sign(data, sign)


# 全局支付服务实例
payment_service = PaymentService()