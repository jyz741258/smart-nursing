from locust import HttpUser, task, between, TaskSet, events
import random
import queue

# ============================================================
# 全局账号池（所有虚拟用户共享，线程安全）
# ============================================================
ACCOUNT_QUEUE = queue.Queue()


@events.init.add_listener
def setup_test_accounts(environment, **kwargs):
    """
    Locust 启动时执行一次：生成 300 个测试账号放入队列
    """
    accounts = []

    # 老人账号：18000000000 ~ 18000000099（100个）
    for i in range(100):
        accounts.append({
            "phone": f"18000000{str(i).zfill(3)}" if i < 1000 else f"18000000{i}",
            "password": "test123456",
            "type": 1,
            "role_name": "老人"
        })

    # 护理员账号：18000000100 ~ 18000000199（100个）
    for i in range(100, 200):
        accounts.append({
            "phone": f"18000000{str(i).zfill(3)}" if i < 1000 else f"18000000{i}",
            "password": "test123456",
            "type": 2,
            "role_name": "护理员"
        })

    # 家属账号：18000000200 ~ 18000000299（100个）
    for i in range(200, 300):
        accounts.append({
            "phone": f"18000000{str(i).zfill(3)}" if i < 1000 else f"18000000{i}",
            "password": "test123456",
            "type": 4,
            "role_name": "家属"
        })

    # 打乱顺序，让不同角色混合进入队列
    random.shuffle(accounts)

    for acc in accounts:
        ACCOUNT_QUEUE.put(acc)

    print(f"✅ 账号池初始化完成，共 {len(accounts)} 个账号（老人:100, 护理员:100, 家属:100）")


# ============================================================
# 1. 老人（Elder）的任务集
# ============================================================
class ElderBehavior(TaskSet):
    @task(10)
    def view_services(self):
        """浏览服务项目（高频）"""
        with self.client.get("/api/services/",
                             name="/api/services [浏览服务]",
                             catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"浏览服务失败: {resp.status_code}")

    @task(5)
    def view_orders(self):
        """查看自己的订单"""
        with self.client.get("/api/orders/",
                             name="/api/orders [查看订单]",
                             catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"查看订单失败: {resp.status_code}")

    @task(3)
    def view_profile(self):
        """查看个人资料"""
        self.client.get("/api/users/profile", name="/api/users/profile [个人资料]")

    @task(2)
    def view_health_metrics(self):
        """查看健康指标"""
        self.client.get("/api/health/metrics", name="/api/health/metrics [健康指标]")

    @task(1)
    def create_order(self):
        """下单（低频但核心）"""
        self.client.post("/api/orders/",
                         json={
                             "service_id": 1,
                             "elder_id": self.user.user_id,
                             "service_time": "2026-04-21T14:00:00",
                             "notes": "老人端测试下单"
                         },
                         name="/api/orders [创建订单]")


# ============================================================
# 2. 护理员（Nurse）的任务集
# ============================================================
class NurseBehavior(TaskSet):
    @task(10)
    def view_available_orders(self):
        """刷待接单列表（核心高频）"""
        with self.client.get("/api/orders/?status=2",
                             name="/api/orders [待接单列表]",
                             catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"获取待接单失败: {resp.status_code}")

    @task(5)
    def view_my_orders(self):
        """查看服务中订单"""
        self.client.get("/api/orders/?status=3", name="/api/orders [服务中订单]")

    @task(3)
    def view_elder_list(self):
        """查看老人列表"""
        self.client.get("/api/users/elder/list", name="/api/users/elder/list [老人列表]")

    @task(2)
    def create_nursing_record(self):
        """创建护理记录"""
        self.client.post("/api/nursing/records",
                         json={
                             "elder_id": 5,  # 后续可改为动态获取
                             "nursing_type": 1,
                             "description": "日常护理记录",
                             "start_time": "2026-04-21T09:00:00"
                         },
                         name="/api/nursing/records [创建护理记录]")

    @task(1)
    def view_workers(self):
        """查看其他护理员"""
        self.client.get("/api/users/workers", name="/api/users/workers [护理员列表]")


# ============================================================
# 3. 家属（Family）的任务集
# ============================================================
class FamilyBehavior(TaskSet):
    @task(10)
    def view_binding_elder(self):
        """查看绑定老人"""
        with self.client.get("/api/users/binding-elder",
                             name="/api/users/binding-elder [查看绑定老人]",
                             catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"查看绑定老人失败: {resp.status_code}")

    @task(5)
    def view_elder_orders(self):
        """查看老人订单"""
        self.client.get("/api/orders/", name="/api/orders [家属-查看老人订单]")

    @task(3)
    def view_elder_health(self):
        """查看老人健康"""
        self.client.get("/api/health/metrics", name="/api/health/metrics [家属-老人健康]")

    @task(2)
    def view_services(self):
        """浏览服务（准备代下单）"""
        self.client.get("/api/services/", name="/api/services [家属-浏览服务]")

    @task(1)
    def create_order_for_elder(self):
        """代老人下单"""
        self.client.post("/api/orders/",
                         json={
                             "service_id": 1,
                             "elder_id": 5,  # 需改为绑定的老人ID
                             "service_time": "2026-04-21T15:00:00",
                             "notes": "家属代下单"
                         },
                         name="/api/orders [家属代下单]")


# ============================================================
# 4. 主用户类（路由器）
# ============================================================
class SmartNursingUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://192.168.61.16:5000"

    def on_start(self):
        """
        从队列领取账号 → 登录 → 按角色挂载任务集
        """
        # 从全局队列领取一个专属账号（如果队列空了会阻塞等待）
        self.account = ACCOUNT_QUEUE.get()

        # 登录
        with self.client.post("/api/users/login",
                              json={
                                  "phone": self.account["phone"],
                                  "password": self.account["password"]
                              },
                              catch_response=True,
                              name="/api/users/login [登录]") as resp:

            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get("data", {}).get("token")
                self.user_id = data.get("data", {}).get("user_id")
                self.user_type = data.get("data", {}).get("user_type")

                if self.token:
                    # 设置全局认证头
                    self.client.headers.update({"Authorization": f"Bearer {self.token}"})

                    # ========== 按角色挂载任务集 ==========
                    if self.user_type == 1:
                        self.tasks = [ElderBehavior]
                    elif self.user_type == 2:
                        self.tasks = [NurseBehavior]
                    elif self.user_type == 4:
                        self.tasks = [FamilyBehavior]

                    resp.success()
                    print(f"✅ {self.account['role_name']} {self.account['phone']} 登录成功")
                else:
                    resp.failure("登录响应中无 token")
                    raise Exception("登录失败，停止该用户")
            else:
                resp.failure(f"登录失败 HTTP {resp.status_code}: {resp.text}")
                raise Exception(f"登录失败: {resp.status_code}")

    def on_stop(self):
        """
        虚拟用户停止时，归还账号到队列，支持压测复用
        """
        if hasattr(self, 'account'):
            ACCOUNT_QUEUE.put(self.account)
            print(f"🔄 归还账号: {self.account['phone']}")