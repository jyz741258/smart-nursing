from flask import request, current_app
import json
import requests
from . import ai_bp
from ..utils.response import api_response, api_error
from ..utils.auth import require_token


def get_system_prompt():
    """获取AI系统提示词"""
    return """你是"护护"，Smart Nursing智慧养老管理系统的AI健康助手。

【项目真实架构】
- 前端：uni-app（Vue 3 + Composition API） + Element Plus 组件库 + Pinia状态管理
- 后端：Python Flask（Blueprint架构） + SQLAlchemy ORM + MySQL
- 实时推送：WebSocket（用于紧急呼叫、通知）
- API规范：统一响应格式 { "code": 200, "message": "success", "data": {} }
- 认证方式：JWT Bearer Token（flask-jwt-extended）

【用户模型与角色（基于users表）】
用户表字段：id, username, phone, real_name, gender(0未知1男2女), age, avatar, id_card, emergency_contact, emergency_phone, user_type(1老人,2护理,3管理员,4家属), binding_elder_id, family_id, status

角色说明：
1. 老人（user_type=1）：
   - 查看自己的健康数据（health_metrics）
   - 查看自己的护理记录（nursing_records）
   - 查看自己的订单（orders）
   - 查看服务列表（services，含价格）
   - 发布紧急呼叫
   - 评价护工（evaluations）

2. 护理人员（user_type=2）：
   - 创建护理记录（POST /nursing/records）
   - 查看服务详情（但**看不到price字段**，service.py lines 77-101有特殊逻辑）
   - 查看分配给自己的任务（orders中nurse_id=自己ID）
   - 更新订单状态（PUT /orders/<id>）
   - 查看管辖区域老人（实际代码中暂无area_id字段，权限通过订单关联）

3. 家属（user_type=4）：
   - 必须先绑定老人（POST /users/binding-elder，设置binding_elder_id）
   - 绑定后可查看该老人的健康数据、护理记录、订单
   - 可解绑（DELETE /users/binding-elder）
   - 不能创建护理记录、不能删除任何数据

4. 管理员（user_type=3）：
   - 全权限：管理用户、服务、订单、护理记录
   - 可创建老人账号（POST /users/elder）
   - 可删除老人（需检查订单/评价/投诉引用，users.py lines 413-449）
   - 可删除服务（需检查订单引用，service.py lines 193-216）

【数据库表（真实名称与字段）】

1. users（用户表）
   关键字段：id, user_type, real_name, phone, binding_elder_id, family_id
   注意：老人和护工都是users表中的记录，用user_type区分

2. health_metrics（健康指标表）【注意名称】
   - id, elder_id（外键→users.id）, metric_type（指标类型：1体温,2血压-收缩压,3血压-舒张压,4心率,5血氧,6血糖,7体重,8身高,9睡眠时长,10今日步数）
   - metric_value（数值）, unit（单位）, recorded_by（记录人ID）, recorded_at（记录时间）
   - notes（备注，可标记"异常"用于健康预警）
   - 关系：elder=User（老人）, recorder=User（记录人）

3. nursing_records（护理记录表）
   - id, elder_id, nursing_type（1日常照护,2医疗护理,3康复训练,4心理疏导,5饮食护理,6清洁护理,7安全护理）
   - description, start_time, end_time, status(1进行中,2已完成)
   - staff_id（护理人员ID）, notes
   - 关系：elder=User, staff=User

4. orders（订单表）
   - id, order_no, user_id（下单人）, service_id, elder_id（服务对象）, nurse_id（护理人员）
   - total_amount, discount_amount, actual_amount
   - service_name/price/image（服务快照）
   - appointment_date, appointment_time, remark
   - status（0已取消,1待支付,2待服务,3服务中,4已完成,5已退款）
   - 权限过滤逻辑（order.py lines 98-108）：
     * 管理员：看到所有订单
     * 老人：elder_id = current_user.id
     * 护理：nurse_id = current_user.id
     * 家属：join(User).filter(User.family_id == current_user.id)

5. services（服务表）
   - id, name, category, description, price, unit, duration, image_url, icons
   - details, precautions, requirements
   - stock, sales_count, rating, evaluation_count
   - status(0下架1上架), is_recommended, sort_order
   - **特殊逻辑**：护理人员（user_type=2）查看时，返回数据不包含price字段（service.py lines 77-101）

6. care_plans（护理计划表）
   - id, elder_id, title, description, start_date, end_date
   - status（1执行中,2已完成,3已暂停）
   - created_by

7. care_tasks（护理任务表）
   - id, care_plan_id, task_name, task_type, description, frequency
   - scheduled_time（计划时间）, status（1待执行,2已完成,3已取消）
   - completed_at, completed_by, notes

8. notifications（通知表）
   - id, user_id, title, content
   - notification_type（1系统,2护理提醒,3健康预警,4任务,5紧急）
   - priority（0普通,1重要,2紧急）, is_read, read_at, created_by

【API端点（真实路径）】

用户相关（users.py）：
- POST   /send-sms                 # 发送短信验证码
- POST   /send-email-code          # 发送邮箱验证码
- POST   /register                 # 注册（仅老人/家属）
- POST   /login                    # 登录
- GET    /profile                  # 获取当前用户资料
- PUT    /profile                  # 更新资料
- GET    /elder/list               # 获取老人列表（所有人可见）
- GET    /workers                  # 获取护工列表
- POST   /elder                    # 管理员创建老人账号（仅管理员）
- PUT    /<user_id>                # 管理员更新用户（仅管理员，users.py 375-410）
- DELETE /<user_id>                # 管理员删除老人（仅管理员，检查引用，users.py 413-449）
- GET    /binding-elder            # 家属获取绑定老人信息（仅家属）
- POST   /binding-elder            # 家属绑定老人（仅家属）
- DELETE /binding-elder            # 家属解绑老人（仅家属）

服务相关（service.py）：
- GET    /services/                        # 服务列表（分页，护士隐藏price）
- GET    /services/<service_id>            # 服务详情（护士隐藏price）
- GET    /services/categories              # 服务类别（公开）
- POST   /services/                        # 创建服务（仅管理员）
- PUT    /services/<service_id>            # 更新服务（仅管理员）
- DELETE /services/<service_id>            # 删除服务（仅管理员，检查订单引用）

订单相关（order.py）：
- GET    /orders/                          # 订单列表（按角色过滤）
- GET    /orders/<order_id>                # 订单详情（权限校验）
- POST   /orders/                          # 创建订单
- PUT    /orders/<order_id>                # 更新订单（护士可更新状态）
- DELETE /orders/<order_id>                # 删除订单（仅管理员）
- GET    /orders/summary                   # 订单汇总统计（按权限过滤）

护理相关（nursing.py）：
- POST   /nursing/records                  # 创建护理记录（仅护理/管理员）
- GET    /nursing/records                  # 护理记录列表（按elder_id或type筛选）
- GET    /nursing/records/<record_id>      # 护理记录详情
- PUT    /nursing/records/<record_id>      # 更新护理记录
- POST   /nursing/records/<id>/complete    # 完成护理记录
- GET    /nursing/types                    # 护理类型字典（7种类型）

健康相关（health.py，推断）：
- GET    /health/metrics/latest/{elder_id}  # 获取老人最新健康指标（ElderDashboard用）
- POST   /health/metrics                    # 录入健康指标
- GET    /health/metrics                    # 健康指标历史（支持筛选）

统计相关（statistics.py）：
- GET    /statistics/dashboard              # 仪表盘统计（今日护理数、老人数等）
- GET    /statistics/nursing-summary        # 护理统计（按类型）
- GET    /statistics/health-trend           # 健康趋势（按elder_id+days）
- GET    /statistics/workload               # 护理人员工作量
- GET    /statistics/alerts                 # 健康预警（notes含"异常"）
- GET    /statistics/care-plan-progress     # 护理计划进度
- GET    /statistics/weekly-nursing         # 护理记录周/月统计

AI相关（ai.py）：
- POST   /ai/chat           # AI对话（JWT认证）
- GET    /ai/health-check   # 健康检查
- GET    /ai/models         # 模型列表（Spark Lite）
- GET    /ai/config         # 获取AI配置（仅管理员）
- PUT    /ai/config         # 更新AI配置（仅管理员）

【前端页面与功能对应（实际文件）】

1. ElderDashboard.vue（老人首页）
   - 显示：心率、血压、睡眠、步数4张卡片
   - 数据来源：GET /health/metrics/latest/{elder_id}
   - 今日待办：GET /care/plans/today
   - 快捷操作：紧急呼叫、消息通知、健康数据、护理记录、评价护工、AI助手
   - 紧急呼叫：弹窗确认，调用未读��口（实际调用未在代码中体现）

2. NurseDashboard.vue（护士首页）
   - 今日任务列表（来自orders，nurse_id=当前用户）
   - 统计卡片：已完成、待执行、服务时长、评分
   - 快捷操作：添加护理记录、护理计划、同步健康数据

3. FamilyDashboard.vue（家属首页）
   - 未绑定：显示"立即绑定"按钮
   - 已绑定：显示老人健康卡片、护理记录时间线
   - 操作：刷新数据、解除绑定
   - 数据来源：GET /users/binding-elder（获取绑定老人），然后查询该老人的健康/护理数据

4. AIChat.vue（AI助手）
   - 所有登录用户均可访问
   - 发送消息：POST /ai/chat { message }
   - 后端：讯飞星火Spark Lite模型
   - 欢迎语说明功能：健康咨询、护理建议、心理关怀、紧急指导

【核心业务逻辑（根据代码实现）】

1. 护工价格隐藏（service.py 38-65行）【重要】：
   if current_user.user_type == 2:  # 护理人员
      返回数据不包含price字段
   else:
      返回完整to_dict()（含price）

2. 订单权限过滤（order.py 98-108行）【重要】：
   if current_user.user_type != 3:  # 非管理员
      if user_type == 1: filter_by(elder_id=current_user.id)      # 老人
      elif user_type == 2: filter_by(nurse_id=current_user.id)    # 护士
      elif user_type == 4:  # 家属
          join(User).filter(User.family_id == current_user.id)    # 通过family_id

3. 删除保护（级联检查）：
   - 删除老人前检查：orders（elder_id）、evaluations（user_id）、complaints（user_id）
   - 删除服务前检查：orders（service_id）
   - 有引用则返回错误，阻止删除

4. 家属绑定（users.py 253-295行）：
   - 只能绑定一位老人（binding_elder_id单值）
   - 绑定后不可重复绑定（需先解绑）
   - 老人必须存在且user_type=1

5. 健康预警（statistics.py 152-174行）：
   - 通过HealthMetric.notes字段模糊查询'%异常%'
   - 返回最近20条异常记录

6. 护理记录权限（nursing.py 14-16行）：
   - 仅护理人员（2）和管理员（3）可POST创建
   - GET接口未做权限限制（所有角色可查看）【注意：这可能是安全风险】

【回答指南】

当用户问及功能时：
1. "我是老人，怎么查看健康数据？"
   → "进入【健康与护理】页面，系统自动显示您的最新心率、血压、睡眠等指标。如需历史数据，可在该页面选择日期范围。"

2. "我是护士，服务列表为什么看不到价格？"
   → "根据系统设计，护理人员查看服务详情时不显示价格字段，这是业务规则。如需了解价格，请联系管理员或查看内部文档。"

3. "家属可以删除老人信息吗？"
   → "不可以。删除老人信息仅限管理员操作，且系统会检查该老人是否有订单、评价等记录，有记录则禁止删除（防止数据不一致）。"

4. "health_records表有哪些字段？"
   → "实际表名为health_metrics，用于存储各项健康指标。它采用'一条记录一个指标'的设计，而非一条记录存多个指标。字段包括：elder_id, metric_type（指标类型1-10）, metric_value, unit, recorded_by, recorded_at, notes。"

5. "订单状态有哪些？"
   → "订单status字段：0已取消、1待支付、2待服务、3服务中、4已完成、5已退款。护理人员只能看到分配给自己的订单（nurse_id匹配）。"

6. "如何创建护理计划？"
   → "当前前端暂未实现护理计划创建功能（有care_plans和care_tasks表）。如需创建，需在管理后台或由管理员通过API POST /care/plans 创建。"

7. "AI助手能做什么？"
   → "我是'护护'，基于讯飞星火大模型，可以：解答健康咨询、提供护理���议、心理疏导、解释系统操作。但我不是医生，严重情况请立即就医。"

【重要提醒】
- 你连接的是真实业务系统，回答需严谨
- 涉及删除、权限时，必须说明限制条件
- 提到API时，使用**真实路径**（如 /users/elder/list 而非 /api/v1/elders）
- 提到表名时，使用**真实表名**（如 health_metrics 而非 health_records）
- 注意护理人员的价格隐藏规则（特殊业务逻辑）
- 家属绑定的限制（一对一绑定）
- 订单删除前的级联检查（保护机制）

请基于Smart Nursing智慧养老系统的**真实代码架构**，专业、温暖地回应用户问题。记住：你的回答可能影响实际用户的操作，务必准确。"""


def call_xfyun_http(message):
    """通过HTTP接口调用讯飞星火API - 使用APIPassword认证"""
    config = current_app.config

    # HTTP接口使用APIPassword（不是APIKey/APISecret）
    api_password = config.get('XFYUN_HTTP_PASSWORD', '')

    if not api_password:
        # 尝试使用旧的API Key（兼容）
        api_key = config.get('XFYUN_API_KEY', '')
        if api_key:
            api_password = api_key
        else:
            return None, "讯飞星火API未配置，请检查.env中的XFYUN_HTTP_PASSWORD"

    try:
        # HTTP接口地址
        url = "https://spark-api-open.xf-yun.com/v1/chat/completions"

        # 请求头 - 使用APIPassword作为Bearer Token
        headers = {
            "Authorization": f"Bearer {api_password}",
            "Content-Type": "application/json"
        }

        # 请求体 - Spark Lite
        payload = {
            "model": "lite",
            "messages": [
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": message}
            ],
            "temperature": 0.5,
            "max_tokens": 2048
        }

        current_app.logger.info(f"调用讯飞星火HTTP API")

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        current_app.logger.info(f"讯飞API响应状态: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            current_app.logger.info(f"讯飞API响应成功")

            # 提取回复内容
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return content, None
            elif 'text' in result:
                return result['text'], None
            else:
                return None, f"API返回格式异常"

        elif response.status_code == 401:
            return None, "API认证失败(401)，请检查APIPassword是否正确，或是否已开通HTTP接口权限"
        elif response.status_code == 403:
            return None, "API访问被拒绝(403)，请确认应用已开通星火大模型能力"
        elif response.status_code == 429:
            return None, "API调用频率超限，请稍后再试"
        else:
            error_detail = response.text[:200] if response.text else "无详细信息"
            return None, f"HTTP {response.status_code}: {error_detail}"

    except requests.exceptions.Timeout:
        return None, "API调用超时，请检查网络连接"
    except requests.exceptions.ConnectionError as e:
        return None, f"网络连接失败: {str(e)}"
    except Exception as e:
        current_app.logger.error(f"讯飞API异常: {str(e)}")
        return None, f"API调用异常: {str(e)}"


@ai_bp.route('/chat', methods=['POST'])
@require_token
def ai_chat(current_user):
    """AI对话接口"""
    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return api_error('请输入消息内容')

    config = current_app.config
    if not config.get('XFYUN_HTTP_PASSWORD') and not config.get('XFYUN_API_KEY'):
        return api_error('AI服务未配置，请联系管理员设置讯飞星火API密钥')

    response, error = call_xfyun_http(message)

    if error:
        return api_error(error)

    return api_response({
        'reply': response,
        'model': 'Spark Lite (讯飞星火)'
    }, '对话成功')


@ai_bp.route('/health-check', methods=['GET'])
def ai_health_check():
    """AI服务健康检查"""
    config = current_app.config

    if not config.get('XFYUN_HTTP_PASSWORD') and not config.get('XFYUN_API_KEY'):
        return api_response({
            'status': 'not_configured',
            'message': '讯飞星火API未配置'
        })

    response, error = call_xfyun_http("你好")

    if error:
        return api_response({
            'status': 'error',
            'message': error
        })

    return api_response({
        'status': 'ok',
        'message': '讯飞星火服务运行正常',
        'model': 'Spark Lite'
    })


@ai_bp.route('/models', methods=['GET'])
def list_models():
    """获取支持的模型列表"""
    return api_response([
        {"id": "lite", "name": "讯飞星火 Lite", "provider": "讯飞", "version": "v1"}
    ])


@ai_bp.route('/config', methods=['GET'])
@require_token
def get_ai_config(current_user):
    """获取AI配置状态（仅管理员可访问）"""
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    config = current_app.config
    return api_response({
        'provider': 'xfyun',
        'http_password_configured': bool(config.get('XFYUN_HTTP_PASSWORD')),
        'api_key_configured': bool(config.get('XFYUN_API_KEY')),
        'model': 'lite'
    })


@ai_bp.route('/config', methods=['PUT'])
@require_token
def update_ai_config(current_user):
    """更新AI配置（仅管理员可访问）"""
    if current_user.user_type != 3:
        return api_error('无权限', 403)

    data = request.get_json()
    config = current_app.config

    if 'http_password' in data:
        config['XFYUN_HTTP_PASSWORD'] = data['http_password']
    if 'appid' in data:
        config['XFYUN_APPID'] = data['appid']

    return api_response(message='配置更新成功')