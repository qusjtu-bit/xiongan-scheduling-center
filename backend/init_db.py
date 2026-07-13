# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建所有表结构并插入基础数据（部门、角色、权限、默认用户）
"""
import os
import sys

# 把项目根目录加入 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, Dept, Role, Permission, Message, Todo, user_role, role_permission
from app.data_models import DataResource, Indicator, IndicatorData, ProjectInfo, BusinessLicense, TransportStation, WaterBody, MunicipalNode, ProjectStage, ApprovalRecord


def init_db():
    """初始化数据库：建表 + 基础数据"""
    app = create_app()
    with app.app_context():
        # 删除旧数据库文件（开发阶段）
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'xiongan.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f'[删除] 旧数据库文件: {db_path}')

        # 建表
        db.create_all()
        print('[建表] 所有表结构创建完成')

        # ========== 1. 部门数据（按真实处室职责分工文件） ==========
        depts = [
            Dept(id=1, parent_id=0, dept_name='雄安新区建设和交通管理局', dept_type=1, sort=1, status=0),
            Dept(id=2, parent_id=1, dept_name='局领导', dept_type=2, sort=1, status=0),
            Dept(id=3, parent_id=1, dept_name='办公室', dept_type=3, sort=2, status=0),
            Dept(id=4, parent_id=1, dept_name='政策法规处', dept_type=3, sort=3, status=0),
            Dept(id=5, parent_id=1, dept_name='政务服务处', dept_type=3, sort=4, status=0),
            Dept(id=6, parent_id=1, dept_name='城乡发展处', dept_type=3, sort=5, status=0),
            Dept(id=7, parent_id=1, dept_name='房屋管理处', dept_type=3, sort=6, status=0),
            Dept(id=8, parent_id=1, dept_name='工程质量安全处', dept_type=3, sort=7, status=0),
            Dept(id=9, parent_id=1, dept_name='建筑市场处', dept_type=3, sort=8, status=0),
            Dept(id=10, parent_id=1, dept_name='综合交通组', dept_type=3, sort=9, status=0),
            Dept(id=11, parent_id=1, dept_name='水利组', dept_type=3, sort=10, status=0),
            Dept(id=12, parent_id=1, dept_name='城市管理处', dept_type=3, sort=11, status=0),
            Dept(id=13, parent_id=1, dept_name='城市建设监察处', dept_type=3, sort=12, status=0),
            Dept(id=14, parent_id=1, dept_name='信息化处', dept_type=3, sort=13, status=0),
        ]
        for d in depts:
            db.session.add(d)
        print(f'[数据] 插入 {len(depts)} 个部门')

        # ========== 2. 角色数据 ==========
        roles = [
            Role(id=1, role_name='局领导', role_code='LEADER', data_scope=1, status=0, remark='全局数据权限'),
            Role(id=2, role_name='处室负责人', role_code='DEPT_HEAD', data_scope=2, status=0, remark='本处室数据权限'),
            Role(id=3, role_name='业务经办人', role_code='OPERATOR', data_scope=4, status=0, remark='本人数据权限'),
            Role(id=4, role_name='系统管理员', role_code='ADMIN', data_scope=1, status=0, remark='系统管理权限'),
            Role(id=5, role_name='访客', role_code='GUEST', data_scope=4, status=0, remark='只读权限'),
        ]
        for r in roles:
            db.session.add(r)
        print(f'[数据] 插入 {len(roles)} 个角色')

        # ========== 3. 权限数据 ==========
        permissions = [
            # 一级菜单
            Permission(id=1, parent_id=0, perm_name='工作台', perm_type=1, perm_code='dashboard', icon='dashboard', sort=1),
            Permission(id=2, parent_id=0, perm_name='全局总览', perm_type=1, perm_code='overview', icon='overview', sort=2),
            Permission(id=3, parent_id=0, perm_name='规建管一体化', perm_type=1, perm_code='project', icon='project', sort=3),
            Permission(id=4, parent_id=0, perm_name='业务专题', perm_type=1, perm_code='topic', icon='topic', sort=4),
            Permission(id=5, parent_id=0, perm_name='智能体', perm_type=1, perm_code='ai', icon='ai', sort=5),
            Permission(id=6, parent_id=0, perm_name='系统管理', perm_type=1, perm_code='system', icon='system', sort=6),
            Permission(id=7, parent_id=0, perm_name='建交数据中枢', perm_type=1, perm_code='data', icon='data', sort=8),
            # 系统管理子菜单
            Permission(id=61, parent_id=6, perm_name='用户管理', perm_type=1, perm_code='system:user', icon='user', sort=1),
            Permission(id=62, parent_id=6, perm_name='部门管理', perm_type=1, perm_code='system:dept', icon='dept', sort=2),
            Permission(id=63, parent_id=6, perm_name='角色管理', perm_type=1, perm_code='system:role', icon='role', sort=3),
            Permission(id=64, parent_id=6, perm_name='权限管理', perm_type=1, perm_code='system:perm', icon='perm', sort=4),
            # 按钮/API权限
            Permission(id=611, parent_id=61, perm_name='用户查看', perm_type=3, perm_code='system:user:list'),
            Permission(id=612, parent_id=61, perm_name='用户新增', perm_type=3, perm_code='system:user:add'),
            Permission(id=613, parent_id=61, perm_name='用户编辑', perm_type=3, perm_code='system:user:update'),
            Permission(id=614, parent_id=61, perm_name='用户删除', perm_type=3, perm_code='system:user:delete'),
            Permission(id=621, parent_id=62, perm_name='部门查看', perm_type=3, perm_code='system:dept:list'),
            Permission(id=622, parent_id=62, perm_name='部门新增', perm_type=3, perm_code='system:dept:add'),
            Permission(id=623, parent_id=62, perm_name='部门编辑', perm_type=3, perm_code='system:dept:update'),
            Permission(id=624, parent_id=62, perm_name='部门删除', perm_type=3, perm_code='system:dept:delete'),
            Permission(id=631, parent_id=63, perm_name='角色查看', perm_type=3, perm_code='system:role:list'),
            Permission(id=632, parent_id=63, perm_name='角色新增', perm_type=3, perm_code='system:role:add'),
            Permission(id=633, parent_id=63, perm_name='角色编辑', perm_type=3, perm_code='system:role:update'),
            Permission(id=634, parent_id=63, perm_name='角色删除', perm_type=3, perm_code='system:role:delete'),
            Permission(id=641, parent_id=64, perm_name='权限查看', perm_type=3, perm_code='system:perm:list'),
        ]
        for p in permissions:
            db.session.add(p)
        print(f'[数据] 插入 {len(permissions)} 个权限')

        # ========== 4. 角色-权限关联 ==========
        # 管理员拥有全部权限
        admin_perms = [(4, p.id) for p in permissions]
        for rid, pid in admin_perms:
            db.session.execute(role_permission.insert().values(role_id=rid, permission_id=pid))
        print(f'[数据] 管理员角色分配 {len(admin_perms)} 个权限')

        # 局领导拥有除系统管理外的所有菜单权限
        leader_perms = [(1, pid) for pid in [1, 2, 3, 4, 5, 7]]
        for rid, pid in leader_perms:
            db.session.execute(role_permission.insert().values(role_id=rid, permission_id=pid))
        print(f'[数据] 局领导角色分配 {len(leader_perms)} 个权限')

        # 处室负责人拥有工作台、全局总览、规建管、业务专题、智能体、数据中枢
        dept_head_perms = [(2, pid) for pid in [1, 2, 3, 4, 5, 7]]
        for rid, pid in dept_head_perms:
            db.session.execute(role_permission.insert().values(role_id=rid, permission_id=pid))

        # 经办人拥有工作台、全局总览、规建管、业务专题、数据中枢
        operator_perms = [(3, pid) for pid in [1, 2, 3, 4, 7]]
        for rid, pid in operator_perms:
            db.session.execute(role_permission.insert().values(role_id=rid, permission_id=pid))

        # ========== 5. 默认用户（覆盖全部12个处室） ==========
        from werkzeug.security import generate_password_hash
        users = [
            # —— 系统管理员 ——
            User(id=1, username='admin', password=generate_password_hash('admin123'),
                 real_name='系统管理员', phone='13800000001', dept_id=14, status=0,
                 remark='信息化处-系统管理员账号'),
            # —— 局领导 ——
            User(id=2, username='zhangju', password=generate_password_hash('zhangju123'),
                 real_name='张局', phone='13800000002', dept_id=2, status=0,
                 remark='局领导账号'),
            # —— 处室负责人（每个处室1名） ——
            User(id=3, username='chenzhuren', password=generate_password_hash('chenzhuren123'),
                 real_name='陈主任', phone='13800000003', dept_id=3, status=0,
                 remark='办公室-处室负责人'),
            User(id=4, username='liuchu', password=generate_password_hash('liuchu123'),
                 real_name='刘处长', phone='13800000004', dept_id=4, status=0,
                 remark='政策法规处-处室负责人'),
            User(id=5, username='yangchu', password=generate_password_hash('yangchu123'),
                 real_name='杨处长', phone='13800000005', dept_id=5, status=0,
                 remark='政务服务处-处室负责人'),
            User(id=6, username='zhouchu', password=generate_password_hash('zhouchu123'),
                 real_name='周处长', phone='13800000006', dept_id=6, status=0,
                 remark='城乡发展处-处室负责人'),
            User(id=7, username='wuchu', password=generate_password_hash('wuchu123'),
                 real_name='吴处长', phone='13800000007', dept_id=7, status=0,
                 remark='房屋管理处-处室负责人'),
            User(id=8, username='lichu', password=generate_password_hash('lichu123'),
                 real_name='李处长', phone='13800000008', dept_id=8, status=0,
                 remark='工程质量安全处-处室负责人'),
            User(id=9, username='zhengchu', password=generate_password_hash('zhengchu123'),
                 real_name='郑处长', phone='13800000009', dept_id=9, status=0,
                 remark='建筑市场处-处室负责人'),
            User(id=10, username='chuchu', password=generate_password_hash('chuchu123'),
                 real_name='褚处长', phone='13800000010', dept_id=10, status=0,
                 remark='综合交通组-处室负责人'),
            User(id=11, username='weichu', password=generate_password_hash('weichu123'),
                 real_name='卫处长', phone='13800000011', dept_id=11, status=0,
                 remark='水利组-处室负责人'),
            User(id=12, username='jiangchu', password=generate_password_hash('jiangchu123'),
                 real_name='蒋处长', phone='13800000012', dept_id=12, status=0,
                 remark='城市管理处-处室负责人'),
            User(id=13, username='shenchu', password=generate_password_hash('shenchu123'),
                 real_name='沈处长', phone='13800000013', dept_id=13, status=0,
                 remark='城市建设监察处-处室负责人'),
            User(id=14, username='hanchu', password=generate_password_hash('hanchu123'),
                 real_name='韩处长', phone='13800000014', dept_id=14, status=0,
                 remark='信息化处-处室负责人'),
            # —— 业务经办人（业务量大的处室各配1名） ——
            User(id=15, username='wangjing', password=generate_password_hash('wangjing123'),
                 real_name='王经办', phone='13800000015', dept_id=6, status=0,
                 remark='城乡发展处-经办人'),
            User(id=16, username='sunjing', password=generate_password_hash('sunjing123'),
                 real_name='孙经办', phone='13800000016', dept_id=8, status=0,
                 remark='工程质量安全处-经办人'),
            User(id=17, username='zhaojiaotong', password=generate_password_hash('zhaojiaotong123'),
                 real_name='赵交通', phone='13800000017', dept_id=10, status=0,
                 remark='综合交通组-经办人'),
            User(id=18, username='fengjing', password=generate_password_hash('fengjing123'),
                 real_name='冯经办', phone='13800000018', dept_id=9, status=0,
                 remark='建筑市场处-经办人'),
        ]
        for u in users:
            db.session.add(u)
        print(f'[数据] 插入 {len(users)} 个用户')

        # ========== 6. 用户-角色关联 ==========
        user_roles = [
            (1, 4),   # admin -> 系统管理员
            (2, 1),   # zhangju -> 局领导
            # 12名处室负责人
            (3, 2),   # chenzhuren -> 处室负责人
            (4, 2),   # liuchu -> 处室负责人
            (5, 2),   # yangchu -> 处室负责人
            (6, 2),   # zhouchu -> 处室负责人
            (7, 2),   # wuchu -> 处室负责人
            (8, 2),   # lichu -> 处室负责人
            (9, 2),   # zhengchu -> 处室负责人
            (10, 2),  # chuchu -> 处室负责人
            (11, 2),  # weichu -> 处室负责人
            (12, 2),  # jiangchu -> 处室负责人
            (13, 2),  # shenchu -> 处室负责人
            (14, 2),  # hanchu -> 处室负责人
            # 4名业务经办人
            (15, 3),  # wangjing -> 业务经办人
            (16, 3),  # sunjing -> 业务经办人
            (17, 3),  # zhaojiaotong -> 业务经办人
            (18, 3),  # fengjing -> 业务经办人
        ]
        for uid, rid in user_roles:
            db.session.execute(user_role.insert().values(user_id=uid, role_id=rid))
        print(f'[数据] 用户-角色关联 {len(user_roles)} 条')

        # ========== 7. 站内消息 Mock 数据（按角色/部门/用户分配可见范围） ==========
        messages = [
            Message(id=1, title='建交协同调度中心正式上线试运行', content='雄安新区建设和交通管理局协同调度中心已进入试运行阶段，各业务处室可通过统一门户登录办理。', msg_type=4, level=1, sender='系统', scope=1, scope_id=0),
            Message(id=2, title='本周全局待办事项汇总', content='全局待办共42项，其中紧急8项、即将逾期5项，请各处分办责任人及时处置。', msg_type=3, level=2, sender='调度中心', scope=2, scope_id=1),
            Message(id=3, title='月度建设运行态势报告已生成', content='6月建设运行态势报告已完成汇总，涵盖城乡建设、交通运输、水利水务、城市管理四大领域，请局领导查阅。', msg_type=1, level=1, sender='综合处', scope=2, scope_id=1),
            Message(id=4, title='【预警】雄安站枢纽片区塔吊监测数据异常', content='物联网平台监测到雄安站枢纽片区某项目塔吊倾角超限，请工程质量安全处立即核查处置。', msg_type=2, level=3, sender='物联网平台', scope=3, scope_id=8),
            Message(id=5, title='深基坑安全隐患未完成整改提醒', content='工程质量安全处辖区3项深基坑安全隐患尚未完成整改，距截止日期还剩2天，请加快闭环。', msg_type=3, level=2, sender='质安监管', scope=3, scope_id=8),
            Message(id=6, title='【预警】启动区X地块棚改项目进度滞后', content='规建管平台监测到启动区X地块棚改项目实际进度较计划滞后12%，请城乡发展处关注。', msg_type=2, level=2, sender='规建管平台', scope=3, scope_id=6),
            Message(id=7, title='今日施工许可申请待审批', content='政务服务处今日收到施工许可申请12件，请在承诺时限内完成审批。', msg_type=3, level=1, sender='审批中心', scope=3, scope_id=5),
            Message(id=8, title='【预警】白洋淀游船客流超阈值', content='交通运行监测显示白洋淀景区游船实时客流超过安全阈值，建议增派运力并加强疏导。', msg_type=2, level=2, sender='交通运行监测', scope=3, scope_id=10),
            Message(id=9, title='【预警】防汛Ⅳ级应急响应启动', content='受强降雨影响，新区启动防汛Ⅳ级应急响应，请水利组密切关注水位、雨情变化。', msg_type=2, level=3, sender='防汛办', scope=3, scope_id=11),
            Message(id=10, title='市政道路井盖异常位移事件派单', content='城市管理平台推送市政道路井盖异常位移事件3起，已自动派单至城市管理处核实处置。', msg_type=2, level=2, sender='城管平台', scope=3, scope_id=12),
            Message(id=11, title='实名制考勤率偏低项目清单已推送', content='建筑市场处辖区实名制考勤率低于85%的项目共5个，请督促整改。', msg_type=3, level=1, sender='建筑市场', scope=3, scope_id=9),
            Message(id=12, title='系统数据同步维护通知', content='信息化处将于今晚22:00对数据中枢进行增量同步维护，期间部分查询可能短暂延迟。', msg_type=4, level=2, sender='运维', scope=2, scope_id=4),
            Message(id=13, title='您的《城乡发展处季度报告》已通过审核', content='您提交的城乡发展处季度分析报告已完成审核，可在报告中心查看。', msg_type=1, level=1, sender='综合处', scope=4, scope_id=15),
            Message(id=14, title='月度隐患排查任务已分派', content='工程质量安全处月度隐患排查治理任务已分派给您，请于本周内完成现场核查。', msg_type=3, level=2, sender='质安监管', scope=4, scope_id=16),
            Message(id=15, title='综合交通组周例会材料收集提醒', content='请于本周五前提交综合交通组周例会所需材料。', msg_type=1, level=1, sender='办公室', scope=4, scope_id=17),
            Message(id=16, title='企业资质初审待您处理', content='建筑市场处转来建筑业企业资质初审材料，请在2个工作日内完成初审。', msg_type=3, level=2, sender='建筑市场', scope=4, scope_id=18),
            Message(id=17, title='雄安CIM平台V2.0底图服务升级完成', content='雄安CIM平台底图服务已升级至V2.0，支持更精细的片区三维底图。', msg_type=4, level=1, sender='CIM平台', scope=1, scope_id=0),
            Message(id=18, title='新版《雄安新区建设工程管理规定》已发布', content='政策法规处发布新版建设工程管理规定，请各业务处室组织学习并遵照执行。', msg_type=1, level=1, sender='政策法规处', scope=3, scope_id=4),
            Message(id=19, title='保障性住房分配方案公示提醒', content='房屋管理处保障性住房分配方案已进入公示期，请注意收集公众反馈。', msg_type=1, level=1, sender='房屋管理处', scope=3, scope_id=7),
            Message(id=20, title='【预警】违法建设巡查线索待核实', content='城市建设监察处收到违法建设巡查线索3条，请尽快核实并依法处置。', msg_type=2, level=2, sender='城建监察', scope=3, scope_id=13),
        ]
        for m in messages:
            db.session.add(m)
        print(f'[数据] 插入 {len(messages)} 条站内消息')

        # ========== 8. 待办任务 Mock 数据 ==========
        todos = [
            Todo(id=1, title='审批：启动区重点工程汛期施工方案', todo_type=1, source_system='规建管平台', urgency=3, due_date='2026-07-10', status=0, link='/project', scope=2, scope_id=1),
            Todo(id=2, title='签批：全局上半年建设运行报告', todo_type=4, source_system='综合处', urgency=2, due_date='2026-07-12', status=0, link='/overview', scope=2, scope_id=1),
            Todo(id=3, title='整改：容东片区深基坑安全隐患', todo_type=2, source_system='质安监管', urgency=3, due_date='2026-07-09', status=0, link='/topic', scope=3, scope_id=8),
            Todo(id=4, title='核查：雄安站枢纽塔吊监测异常', todo_type=2, source_system='物联网平台', urgency=3, due_date='2026-07-08', status=0, link='/topic', scope=3, scope_id=8),
            Todo(id=5, title='备案：月度隐患排查治理台账', todo_type=3, source_system='质安监管', urgency=1, due_date='2026-07-15', status=0, link='/todos', scope=3, scope_id=8),
            Todo(id=6, title='审批：棚改项目二期施工许可', todo_type=1, source_system='审批中心', urgency=2, due_date='2026-07-11', status=0, link='/todos', scope=3, scope_id=6),
            Todo(id=7, title='报告：城乡发展处二季度工作小结', todo_type=4, source_system='城乡发展处', urgency=1, due_date='2026-07-20', status=0, link='/todos', scope=3, scope_id=6),
            Todo(id=8, title='整改：启动区X地块进度滞后', todo_type=2, source_system='规建管平台', urgency=2, due_date='2026-07-13', status=0, link='/topic', scope=3, scope_id=6),
            Todo(id=9, title='审批：今日施工许可申请12件', todo_type=1, source_system='审批中心', urgency=2, due_date='2026-07-08', status=0, link='/todos', scope=3, scope_id=5),
            Todo(id=10, title='备案：消防验收备案8件', todo_type=3, source_system='政务服务处', urgency=1, due_date='2026-07-14', status=0, link='/todos', scope=3, scope_id=5),
            Todo(id=11, title='整改：白洋淀游船客流超阈值', todo_type=2, source_system='交通运行监测', urgency=2, due_date='2026-07-10', status=0, link='/topic', scope=3, scope_id=10),
            Todo(id=12, title='审批：公交线路优化方案', todo_type=1, source_system='交通运输', urgency=1, due_date='2026-07-18', status=0, link='/todos', scope=3, scope_id=10),
            Todo(id=13, title='审批：建筑业企业资质初审', todo_type=1, source_system='建筑市场', urgency=2, due_date='2026-07-12', status=0, link='/todos', scope=3, scope_id=9),
            Todo(id=14, title='核查：实名制考勤率低于85%项目', todo_type=2, source_system='建筑市场', urgency=1, due_date='2026-07-16', status=0, link='/topic', scope=3, scope_id=9),
            Todo(id=15, title='处置：防汛Ⅳ级应急响应', todo_type=2, source_system='防汛办', urgency=3, due_date='2026-07-08', status=0, link='/topic', scope=3, scope_id=11),
            Todo(id=16, title='报告：河湖长制月度巡查报告', todo_type=4, source_system='水利组', urgency=1, due_date='2026-07-22', status=0, link='/todos', scope=3, scope_id=11),
            Todo(id=17, title='整改：市政道路井盖异常位移3起', todo_type=2, source_system='城管平台', urgency=2, due_date='2026-07-11', status=0, link='/topic', scope=3, scope_id=12),
            Todo(id=18, title='核查：违法建设巡查线索3条', todo_type=2, source_system='城建监察', urgency=2, due_date='2026-07-13', status=0, link='/topic', scope=3, scope_id=13),
            Todo(id=19, title='报告：局务会材料收集', todo_type=4, source_system='办公室', urgency=1, due_date='2026-07-19', status=0, link='/todos', scope=3, scope_id=3),
            Todo(id=20, title='备案：规范性文件备案', todo_type=3, source_system='政策法规处', urgency=1, due_date='2026-07-21', status=0, link='/todos', scope=3, scope_id=4),
            Todo(id=21, title='提交：城乡发展处季度报告', todo_type=4, source_system='城乡发展处', urgency=1, due_date='2026-07-17', status=0, link='/todos', scope=4, scope_id=15),
            Todo(id=22, title='完成：月度隐患排查治理', todo_type=2, source_system='质安监管', urgency=2, due_date='2026-07-09', status=0, link='/todos', scope=4, scope_id=16),
            Todo(id=23, title='初审：建筑业企业资质材料', todo_type=1, source_system='建筑市场', urgency=2, due_date='2026-07-12', status=0, link='/todos', scope=4, scope_id=18),
            Todo(id=24, title='配置：数据同步任务调度', todo_type=5, source_system='运维', urgency=1, due_date='2026-07-25', status=0, link='/system', scope=2, scope_id=4),
            Todo(id=25, title='整改：过往安全通报未闭环项', todo_type=2, source_system='质安监管', urgency=2, due_date='2026-07-01', status=2, link='/topic', scope=3, scope_id=8),
        ]
        for t in todos:
            db.session.add(t)
        print(f'[数据] 插入 {len(todos)} 条待办任务')

        # ========== 9. 数据资源目录 ==========
        resources = [
            DataResource(code='proj_list', name='城建项目信息', domain=1, source_system='规建管一体化平台',
                         table_name='dc_project', update_freq='每日', record_count=8,
                         description='雄安新区在建和已竣工城建项目基本信息，包含房建、市政、交通、水利等类型',
                         fields_schema='[{"name":"项目名称","key":"name"},{"name":"项目类型","key":"ptype"},{"name":"片区","key":"area"},{"name":"建设单位","key":"build_unit"},{"name":"投资额","key":"invest"},{"name":"阶段","key":"stage"}]'),
            DataResource(code='biz_list', name='建筑业企业信息', domain=1, source_system='建筑市场监管平台',
                         table_name='dc_business', update_freq='每日', record_count=8,
                         description='新区注册建筑业企业基本信息，含资质等级、类别、从业人员',
                         fields_schema='[{"name":"企业名称","key":"name"},{"name":"资质等级","key":"cert_level"},{"name":"资质类别","key":"cert_type"},{"name":"片区","key":"area"},{"name":"从业人数","key":"workers"}]'),
            DataResource(code='bus_station', name='公交站点信息', domain=2, source_system='交通运行监测平台',
                         table_name='dc_bus_station', update_freq='每日', record_count=10,
                         description='雄安新区公交站点分布、途经线路与客流数据',
                         fields_schema='[{"name":"站点名称","key":"name"},{"name":"途经线路","key":"lines"},{"name":"片区","key":"area"},{"name":"日均客流","key":"daily_flow"}]'),
            DataResource(code='water_list', name='河湖基本信息', domain=3, source_system='水文监测系统',
                         table_name='dc_water', update_freq='每日', record_count=6,
                         description='新区主要河湖、水库基础信息与水质水位数据',
                         fields_schema='[{"name":"河湖名称","key":"name"},{"name":"类型","key":"wtype"},{"name":"片区","key":"area"},{"name":"水域面积","key":"water_area"},{"name":"水质","key":"quality"},{"name":"水位","key":"level"}]'),
            DataResource(code='muni_list', name='市政设施信息', domain=4, source_system='城管综合平台',
                         table_name='dc_municipal', update_freq='每日', record_count=10,
                         description='市政道路、桥梁、管廊、井盖、路灯等设施分布与运行状态',
                         fields_schema='[{"name":"设施名称","key":"name"},{"name":"类型","key":"ftype"},{"name":"片区","key":"area"},{"name":"状态","key":"status"}]'),
            DataResource(code='idx_proj', name='城乡建设统计指标', domain=1, source_system='数据中枢',
                         table_name='dc_indicator_data', update_freq='每日', record_count=15,
                         description='在建项目数/施工许可/消防验收/隐患/考勤/绿建/造价/投资等15项核心指标'),
            DataResource(code='idx_trans', name='交通运输统计指标', domain=2, source_system='数据中枢',
                         table_name='dc_indicator_data', update_freq='每日', record_count=15,
                         description='路网里程/拥堵指数/公交客流/准点率/事故/新能源车等15项核心指标'),
            DataResource(code='idx_water', name='水利水务统计指标', domain=3, source_system='数据中枢',
                         table_name='dc_indicator_data', update_freq='每日', record_count=13,
                         description='河湖数量/水质达标率/水位/雨量/泵站/供水/污水/防汛等13项核心指标'),
            DataResource(code='idx_muni', name='城市管理统计指标', domain=4, source_system='数据中枢',
                         table_name='dc_indicator_data', update_freq='每日', record_count=12,
                         description='环卫/市容/路灯/井盖/管廊/供热/燃气/绿地/公园等12项核心指标'),
            DataResource(code='idx_overview', name='全局综合指标', domain=5, source_system='数据中枢',
                         table_name='dc_indicator_data', update_freq='每日', record_count=8,
                         description='跨领域综合指标：总投资/总里程/总客流/综合达标率等'),
            DataResource(code='cert_rec', name='施工许可证信息', domain=1, source_system='审批中心',
                         table_name='-', update_freq='实时', record_count=0,
                         description='施工许可证发放记录（待 Step 5 规建管模块完成数据对接）'),
        ]
        for r in resources:
            db.session.add(r)
        print(f'[数据] 插入 {len(resources)} 条数据资源目录')

        # ========== 10. 标准指标定义（≥50项，四大领域）==========
        indicators = [
            Indicator(code='cj01', name='在建项目数', domain=1, unit='个', sort=1, definition='当前在建工程项目总数', calc_expr='COUNT(DISTINCT project_id) FROM dc_project WHERE stage="建设"'),
            Indicator(code='cj02', name='施工许可发放数', domain=1, unit='件', sort=2, definition='本月发放施工许可证数量', calc_expr='COUNT(*) FROM cert_rec WHERE MONTH=当前月'),
            Indicator(code='cj03', name='消防验收通过率', domain=1, unit='%', sort=3, definition='消防验收通过项目占比', calc_expr='通过数/受理数×100'),
            Indicator(code='cj04', name='工程隐患数', domain=1, unit='个', sort=4, definition='在建工程尚存安全隐患数量', calc_expr='COUNT(*) FROM safety_hazard WHERE status="未整改"'),
            Indicator(code='cj05', name='整改闭环率', domain=1, unit='%', sort=5, definition='隐患整改完成比例', calc_expr='已整改/隐患总数×100'),
            Indicator(code='cj06', name='实名制考勤率', domain=1, unit='%', sort=6, definition='在建项目实名制考勤达标率', calc_expr='达标项目/总项目×100'),
            Indicator(code='cj07', name='建筑业总产值', domain=1, unit='亿元', sort=7, definition='季度建筑业生产总值', calc_expr='SUM(产值) FROM biz_stats'),
            Indicator(code='cj08', name='绿建项目占比', domain=1, unit='%', sort=8, definition='绿色建筑项目占新建项目比例', calc_expr='绿建数/新建总数×100'),
            Indicator(code='cj09', name='装配式建筑占比', domain=1, unit='%', sort=9, definition='装配式建筑面积占新建面积比例', calc_expr='装配式面积/新建总面积×100'),
            Indicator(code='cj10', name='危房改造完成率', domain=1, unit='%', sort=10, definition='农村危房改造任务完成比例', calc_expr='完成数/任务数×100'),
            Indicator(code='cj11', name='建筑垃圾备案数', domain=1, unit='件', sort=11, definition='建筑垃圾处理方案备案累计数', calc_expr='COUNT(*) FROM waste_record'),
            Indicator(code='cj12', name='造价信息发布数', domain=1, unit='条', sort=12, definition='工程造价信息发布条目数', calc_expr='COUNT(*) FROM cost_pub'),
            Indicator(code='cj13', name='档案验收完成数', domain=1, unit='件', sort=13, definition='城建档案验收完成项目数', calc_expr='COUNT(*) FROM archive WHERE status="已验收"'),
            Indicator(code='cj14', name='建设投资总额', domain=1, unit='亿元', sort=14, definition='在建项目计划总投资额', calc_expr='SUM(invest) FROM dc_project'),
            Indicator(code='cj15', name='竣工面积', domain=1, unit='万m²', sort=15, definition='本年度竣工建筑总面积', calc_expr='SUM(area) FROM dc_project WHERE stage="运维"'),
            Indicator(code='jt01', name='路网总里程', domain=2, unit='km', sort=1, definition='新区路网总里程（含在建）', calc_expr='SUM(length) FROM road'),
            Indicator(code='jt02', name='拥堵指数', domain=2, unit='-', sort=2, definition='主要路段交通拥堵综合评价指数', calc_expr='AVG(congestion_index) FROM road_section'),
            Indicator(code='jt03', name='公交线路数', domain=2, unit='条', sort=3, definition='正在运营公交线路总数', calc_expr='COUNT(DISTINCT line_no) FROM bus_line'),
            Indicator(code='jt04', name='公交站点覆盖率', domain=2, unit='%', sort=4, definition='500米公交站点覆盖面积比例', calc_expr='覆盖面积/建成区总面积×100'),
            Indicator(code='jt05', name='公交日均客流', domain=2, unit='万人次', sort=5, definition='公交系统日均客运量', calc_expr='SUM(daily_flow) FROM bus_station / 10000'),
            Indicator(code='jt06', name='公交准点率', domain=2, unit='%', sort=6, definition='公交班次准点到达比例', calc_expr='准点班次/总班次×100'),
            Indicator(code='jt07', name='营运车辆数', domain=2, unit='辆', sort=7, definition='注册营运车辆总数', calc_expr='COUNT(*) FROM vehicle'),
            Indicator(code='jt08', name='非法营运查处数', domain=2, unit='件', sort=8, definition='非法营运案件查处累计数', calc_expr='COUNT(*) FROM illegal_case'),
            Indicator(code='jt09', name='交通事故起数', domain=2, unit='起', sort=9, definition='月度交通运输事故起数', calc_expr='COUNT(*) FROM accident'),
            Indicator(code='jt10', name='雄安站日均客流', domain=2, unit='人次', sort=10, definition='雄安站铁路日均到发客流量', calc_expr='AVG(daily_flow) FROM station_stats WHERE name="雄安站"'),
            Indicator(code='jt11', name='白洋淀船舶数', domain=2, unit='艘', sort=11, definition='白洋淀注册在册船舶总数', calc_expr='COUNT(*) FROM ship'),
            Indicator(code='jt12', name='港口岸线利用率', domain=2, unit='%', sort=12, definition='港口岸线已利用长度占比', calc_expr='已利用/总岸线×100'),
            Indicator(code='jt13', name='停车场泊位数', domain=2, unit='个', sort=13, definition='公共停车场总泊位数', calc_expr='SUM(capacity) FROM parking'),
            Indicator(code='jt14', name='新能源公交占比', domain=2, unit='%', sort=14, definition='新能源公交车占总公交车比例', calc_expr='新能源/总数×100'),
            Indicator(code='jt15', name='全市出租车数', domain=2, unit='辆', sort=15, definition='在册出租车总数', calc_expr='COUNT(*) FROM taxi'),
            Indicator(code='sl01', name='河湖数量', domain=3, unit='条/个', sort=1, definition='新区主要河湖水库总数量', calc_expr='COUNT(DISTINCT name) FROM dc_water'),
            Indicator(code='sl02', name='水质达标率', domain=3, unit='%', sort=2, definition='水质监测断面达标比例', calc_expr='达标断面/总断面×100'),
            Indicator(code='sl03', name='河湖长巡查次数', domain=3, unit='次', sort=3, definition='月度河湖长巡查总次数', calc_expr='COUNT(*) FROM patrol_record'),
            Indicator(code='sl04', name='水位超警次数', domain=3, unit='次', sort=4, definition='水位超警戒线事件次数', calc_expr='COUNT(*) FROM water_alarm'),
            Indicator(code='sl05', name='雨量监测站数', domain=3, unit='个', sort=5, definition='雨量自动监测站总数', calc_expr='COUNT(*) FROM rain_station'),
            Indicator(code='sl06', name='泵站运行率', domain=3, unit='%', sort=6, definition='排涝泵站正常运行比例', calc_expr='正常泵站/总泵站×100'),
            Indicator(code='sl07', name='供水管网漏损率', domain=3, unit='%', sort=7, definition='城市供水管网综合漏损比例', calc_expr='漏损量/供水量×100'),
            Indicator(code='sl08', name='污水厂处理率', domain=3, unit='%', sort=8, definition='污水处理厂满负荷运行比例', calc_expr='日处理量/设计能力×100'),
            Indicator(code='sl09', name='用水总量', domain=3, unit='亿m³', sort=9, definition='年度用水总量统计', calc_expr='SUM(water_used) FROM water_stats'),
            Indicator(code='sl10', name='节水指标达标率', domain=3, unit='%', sort=10, definition='节水型社会指标达标比例', calc_expr='达标项数/考核项数×100'),
            Indicator(code='sl11', name='地下水水位', domain=3, unit='m', sort=11, definition='地下水监测平均水位', calc_expr='AVG(level) FROM groundwater'),
            Indicator(code='sl12', name='水土流失治理率', domain=3, unit='%', sort=12, definition='水土流失已治理面积占比', calc_expr='已治理/流失总面积×100'),
            Indicator(code='sl13', name='防汛物资储备率', domain=3, unit='%', sort=13, definition='防汛物资实际储备与计划比例', calc_expr='实际/计划×100'),
            Indicator(code='cg01', name='环卫覆盖率', domain=4, unit='%', sort=1, definition='环卫作业覆盖建成区面积比例', calc_expr='覆盖面积/建成区×100'),
            Indicator(code='cg02', name='垃圾分类点', domain=4, unit='个', sort=2, definition='垃圾分类投放点总数', calc_expr='COUNT(*) FROM waste_station'),
            Indicator(code='cg03', name='日均清运量', domain=4, unit='吨', sort=3, definition='生活垃圾日均清运量', calc_expr='AVG(daily_volume) FROM waste_transport'),
            Indicator(code='cg04', name='道路完好率', domain=4, unit='%', sort=4, definition='市政道路路面完好比例', calc_expr='完好里程/总里程×100'),
            Indicator(code='cg05', name='路灯亮灯率', domain=4, unit='%', sort=5, definition='市政路灯正常亮灯比例', calc_expr='亮灯数/总数×100'),
            Indicator(code='cg06', name='井盖完好率', domain=4, unit='%', sort=6, definition='市政井盖完好无异常比例', calc_expr='完好数/总数×100'),
            Indicator(code='cg07', name='管廊运营里程', domain=4, unit='km', sort=7, definition='综合管廊投入运营总里程', calc_expr='SUM(length) FROM pipe_gallery WHERE status="运营"'),
            Indicator(code='cg08', name='管廊入廊管线', domain=4, unit='条', sort=8, definition='综合管廊内容纳管线总数', calc_expr='COUNT(*) FROM pipe_line WHERE in_gallery=1'),
            Indicator(code='cg09', name='供热管网覆盖率', domain=4, unit='%', sort=9, definition='集中供热管网覆盖面积比例', calc_expr='覆盖面积/建成区×100'),
            Indicator(code='cg10', name='燃气监测异常数', domain=4, unit='次', sort=10, definition='燃气管网监测异常事件次数', calc_expr='COUNT(*) FROM gas_alarm WHERE MONTH=当前月'),
            Indicator(code='cg11', name='绿地覆盖率', domain=4, unit='%', sort=11, definition='建成区绿化覆盖面积比例', calc_expr='绿地面积/建成区×100'),
            Indicator(code='cg12', name='公园数量', domain=4, unit='个', sort=12, definition='已建成城市公园总数', calc_expr='COUNT(*) FROM park'),
        ]
        for ind in indicators:
            db.session.add(ind)
        print(f'[数据] 插入 {len(indicators)} 个标准指标')

        # ========== 11. 指标月度数据（最新一期）==========
        import random
        random.seed(42)
        for ind in indicators:
            base = {'cj01': 42, 'cj02': 128, 'cj03': 94.5, 'cj04': 78, 'cj05': 87.2, 'cj06': 91.3, 'cj07': 56.8,
                    'cj08': 62.5, 'cj09': 38.7, 'cj10': 82.1, 'cj11': 215, 'cj12': 46, 'cj13': 19,
                    'cj14': 328.5, 'cj15': 86.2,
                    'jt01': 428, 'jt02': 1.25, 'jt03': 38, 'jt04': 82.5, 'jt05': 12.6, 'jt06': 91.8,
                    'jt07': 2860, 'jt08': 47, 'jt09': 3, 'jt10': 18500, 'jt11': 320, 'jt12': 68.5,
                    'jt13': 12500, 'jt14': 72, 'jt15': 1560,
                    'sl01': 28, 'sl02': 89.2, 'sl03': 312, 'sl04': 5, 'sl05': 48,
                    'sl06': 96.8, 'sl07': 9.5, 'sl08': 95.2, 'sl09': 2.8,
                    'sl10': 85.6, 'sl11': 8.2, 'sl12': 72.5, 'sl13': 94.3,
                    'cg01': 95.6, 'cg02': 620, 'cg03': 680, 'cg04': 97.8, 'cg05': 98.5,
                    'cg06': 96.2, 'cg07': 68, 'cg08': 142, 'cg09': 88.5,
                    'cg10': 12, 'cg11': 42.8, 'cg12': 18}.get(ind.code, 50)
            val = round(base * random.uniform(0.92, 1.08), 2)
            db.session.add(IndicatorData(indicator_code=ind.code, period='2026-06', value=val))
        print(f'[数据] 插入 {len(indicators)} 条指标数据')

        # ========== 12. 四大主题库 Mock 数据 ==========
        # 城建项目（8条）
        projects = [
            ProjectInfo(id=1, name='雄安城际站及国贸中心TOD综合体', ptype='房建', area='启动区',
                        build_unit='雄安集团城发公司', contractor='中国建筑八局', supervisor='河北工程监理',
                        invest=850000, scale=128.6, scale_unit='万m²',
                        stage='建设', progress=65, start_date='2024-03', plan_end_date='2027-06',
                        lng=116.1086, lat=39.0496),
            ProjectInfo(id=2, name='启动区西北部社区中心', ptype='房建', area='启动区',
                        build_unit='中国雄安集团', contractor='中建三局', supervisor='中咨监理',
                        invest=320000, scale=52.3, scale_unit='万m²',
                        stage='建设', progress=42, start_date='2024-09', plan_end_date='2026-12',
                        lng=116.095, lat=39.058),
            ProjectInfo(id=3, name='容东片区E组团安置房', ptype='房建', area='容东片区',
                        build_unit='雄安集团城发公司', contractor='中铁建设', supervisor='北京监理',
                        invest=480000, scale=86.0, scale_unit='万m²',
                        stage='运维', progress=100, start_date='2022-05', plan_end_date='2024-10',
                        actual_end_date='2024-09',
                        lng=116.10, lat=39.045),
            ProjectInfo(id=4, name='雄安新区至北京大兴机场快线(R1线)', ptype='交通', area='起步区',
                        build_unit='河北轨道公司', contractor='中国中铁', supervisor='铁科院监理',
                        invest=1850000, scale=86.2, scale_unit='km',
                        stage='建设', progress=78, start_date='2023-06', plan_end_date='2026-06',
                        lng=116.108, lat=39.038),
            ProjectInfo(id=5, name='起步区EA1东延市政道路工程', ptype='市政', area='起步区',
                        build_unit='中国交建', contractor='中交一公局', supervisor='中交监理',
                        invest=95000, scale=12.8, scale_unit='km',
                        stage='建设', progress=55, start_date='2025-01', plan_end_date='2026-08',
                        lng=116.125, lat=39.042),
            ProjectInfo(id=6, name='雄安站综合交通枢纽配套工程', ptype='交通', area='昝岗片区',
                        build_unit='雄安集团交通公司', contractor='中铁建工', supervisor='铁四院监理',
                        invest=620000, scale=45.0, scale_unit='万m²',
                        stage='运维', progress=100, start_date='2022-08', plan_end_date='2024-06',
                        actual_end_date='2024-05',
                        lng=116.160, lat=39.055),
            ProjectInfo(id=7, name='白洋淀生态清淤四期工程', ptype='水利', area='白洋淀',
                        build_unit='中交天津航道局', contractor='中交天航', supervisor='天津水运监理',
                        invest=126000, scale=68.5, scale_unit='km²',
                        stage='建设', progress=38, start_date='2025-06', plan_end_date='2027-03',
                        lng=116.06, lat=38.93),
            ProjectInfo(id=8, name='悦容公园二期景观工程', ptype='园林', area='容东片区',
                        build_unit='中国建筑', contractor='中建园林', supervisor='河北园林监理',
                        invest=58000, scale=2.8, scale_unit='km²',
                        stage='建设', progress=82, start_date='2024-11', plan_end_date='2026-03',
                        lng=116.088, lat=39.052),
        ]
        for p in projects:
            db.session.add(p)
        print(f'[数据] 插入 {len(projects)} 个城建项目')

        # 项目阶段里程碑（每个项目6个阶段）
        stages_data = [
            # 项目1: 雄安城际站TOD — 建设阶段
            (1, '立项', 1, '2023-06', '2023-09', '2023-09', '已完成'),
            (1, '规划', 2, '2023-09', '2023-12', '2023-12', '已完成'),
            (1, '审批', 3, '2023-12', '2024-03', '2024-02', '已完成'),
            (1, '建设', 4, '2024-03', '2027-06', None, '进行中'),
            (1, '验收', 5, '2027-06', '2027-09', None, '未开始'),
            (1, '运维', 6, '2027-09', '', None, '未开始'),
            # 项目2: 社区中心 — 建设中
            (2, '立项', 1, '2024-03', '2024-06', '2024-06', '已完成'),
            (2, '规划', 2, '2024-06', '2024-08', '2024-08', '已完成'),
            (2, '审批', 3, '2024-08', '2024-09', '2024-09', '已完成'),
            (2, '建设', 4, '2024-09', '2026-12', None, '进行中'),
            (2, '验收', 5, '2026-12', '2027-03', None, '未开始'),
            (2, '运维', 6, '2027-03', '', None, '未开始'),
            # 项目3: 安置房 — 已竣工
            (3, '立项', 1, '2021-10', '2022-01', '2022-01', '已完成'),
            (3, '规划', 2, '2022-01', '2022-04', '2022-03', '已完成'),
            (3, '审批', 3, '2022-03', '2022-05', '2022-05', '已完成'),
            (3, '建设', 4, '2022-05', '2024-10', '2024-08', '已完成'),
            (3, '验收', 5, '2024-08', '2024-09', '2024-09', '已完成'),
            (3, '运维', 6, '2024-09', '', None, '进行中'),
            # 项目4: R1线
            (4, '立项', 1, '2022-12', '2023-03', '2023-03', '已完成'),
            (4, '规划', 2, '2023-03', '2023-06', '2023-06', '已完成'),
            (4, '审批', 3, '2023-06', '2023-08', '2023-07', '已完成'),
            (4, '建设', 4, '2023-08', '2026-06', None, '进行中'),
            (4, '验收', 5, '2026-06', '2026-09', None, '未开始'),
            (4, '运维', 6, '2026-09', '', None, '未开始'),
            # 项目5: EA1东延
            (5, '立项', 1, '2024-06', '2024-09', '2024-09', '已完成'),
            (5, '规划', 2, '2024-09', '2024-11', '2024-11', '已完成'),
            (5, '审批', 3, '2024-11', '2025-01', '2024-12', '已完成'),
            (5, '建设', 4, '2025-01', '2026-08', None, '进行中'),
            (5, '验收', 5, '2026-08', '2026-10', None, '未开始'),
            (5, '运维', 6, '2026-10', '', None, '未开始'),
            # 项目6: 雄安站枢纽 — 已竣工
            (6, '立项', 1, '2021-09', '2022-02', '2022-02', '已完成'),
            (6, '规划', 2, '2022-02', '2022-05', '2022-05', '已完成'),
            (6, '审批', 3, '2022-05', '2022-08', '2022-07', '已完成'),
            (6, '建设', 4, '2022-08', '2024-06', '2024-04', '已完成'),
            (6, '验收', 5, '2024-04', '2024-05', '2024-05', '已完成'),
            (6, '运维', 6, '2024-05', '', None, '进行中'),
            # 项目7: 白洋淀清淤
            (7, '立项', 1, '2025-01', '2025-03', '2025-03', '已完成'),
            (7, '规划', 2, '2025-03', '2025-05', '2025-05', '已完成'),
            (7, '审批', 3, '2025-05', '2025-06', '2025-06', '已完成'),
            (7, '建设', 4, '2025-06', '2027-03', None, '进行中'),
            (7, '验收', 5, '2027-03', '2027-05', None, '未开始'),
            (7, '运维', 6, '2027-05', '', None, '未开始'),
            # 项目8: 悦容公园
            (8, '立项', 1, '2024-06', '2024-08', '2024-08', '已完成'),
            (8, '规划', 2, '2024-08', '2024-10', '2024-10', '已完成'),
            (8, '审批', 3, '2024-10', '2024-11', '2024-11', '已完成'),
            (8, '建设', 4, '2024-11', '2026-03', None, '进行中'),
            (8, '验收', 5, '2026-03', '2026-05', None, '未开始'),
            (8, '运维', 6, '2026-05', '', None, '未开始'),
        ]
        for (pid, name, order, start, plan_end, actual_end, status) in stages_data:
            db.session.add(ProjectStage(project_id=pid, stage_name=name, stage_order=order,
                                         start_date=start, plan_end_date=plan_end,
                                         actual_end_date=actual_end, status=status))
        print(f'[数据] 插入 {len(stages_data)} 条阶段里程碑')

        # 审批记录（每个在建项目2-4条）
        approvals = [
            ApprovalRecord(id=1, project_id=1, approval_type='施工许可', apply_date='2024-01-15', approve_date='2024-02-20', status='已通过', approver='政务服务处'),
            ApprovalRecord(id=2, project_id=1, approval_type='消防设计审查', apply_date='2024-02-25', approve_date='2024-03-10', status='已通过', approver='工程质量安全处'),
            ApprovalRecord(id=3, project_id=1, approval_type='水土保持方案', apply_date='2024-03-01', approve_date='2024-03-18', status='已通过', approver='水利组'),
            ApprovalRecord(id=4, project_id=2, approval_type='施工许可', apply_date='2024-07-10', approve_date='2024-08-05', status='已通过', approver='政务服务处'),
            ApprovalRecord(id=5, project_id=4, approval_type='施工许可', apply_date='2023-05-20', approve_date='2023-06-15', status='已通过', approver='政务服务处'),
            ApprovalRecord(id=6, project_id=4, approval_type='环评批复', apply_date='2023-04-10', approve_date='2023-05-08', status='已通过', approver='环保局'),
            ApprovalRecord(id=7, project_id=5, approval_type='施工许可', apply_date='2024-12-01', approve_date='2024-12-20', status='已通过', approver='政务服务处'),
            ApprovalRecord(id=8, project_id=7, approval_type='施工许可', apply_date='2025-04-15', approve_date='2025-05-10', status='已通过', approver='政务服务处'),
            ApprovalRecord(id=9, project_id=7, approval_type='水行政许可', apply_date='2025-04-20', approve_date='2025-05-15', status='已通过', approver='水利组'),
            ApprovalRecord(id=10, project_id=8, approval_type='园林方案审批', apply_date='2024-09-01', approve_date='2024-10-10', status='已通过', approver='城市管理处'),
            # 待审批/预警项
            ApprovalRecord(id=11, project_id=2, approval_type='消防验收', apply_date='2026-06-15', approve_date=None, status='待审批', approver='工程质量安全处'),
            ApprovalRecord(id=12, project_id=5, approval_type='道路竣工验收', apply_date='2026-07-01', approve_date=None, status='待审批', approver='政务服务处'),
            # 已驳回项
            ApprovalRecord(id=13, project_id=4, approval_type='临时用地审批', apply_date='2025-11-10', approve_date='2025-11-25', status='已驳回', approver='城乡发展处', remark='用地范围需调整'),
        ]
        for a in approvals:
            db.session.add(a)
        print(f'[数据] 插入 {len(approvals)} 条审批记录')

        # 建筑业企业（8条）
        businesses = [
            BusinessLicense(id=1, name='雄安新区城市发展有限公司', cert_level='特级', cert_type='建筑工程总承包',
                            area='容东片区', workers=2850),
            BusinessLicense(id=2, name='河北建工集团雄安公司', cert_level='一级', cert_type='建筑工程总承包',
                            area='容城县城', workers=1620),
            BusinessLicense(id=3, name='中国铁建雄安项目部', cert_level='一级', cert_type='市政工程总承包',
                            area='启动区', workers=980),
            BusinessLicense(id=4, name='中交雄安投资有限公司', cert_level='一级', cert_type='公路工程总承包',
                            area='昝岗片区', workers=1340),
            BusinessLicense(id=5, name='雄安新区路桥建设有限公司', cert_level='二级', cert_type='公路工程总承包',
                            area='雄县县城', workers=520),
            BusinessLicense(id=6, name='保定水利工程局雄安分公司', cert_level='一级', cert_type='水利水电总承包',
                            area='安新县城', workers=780),
            BusinessLicense(id=7, name='雄安中建八局分公司', cert_level='特级', cert_type='建筑工程总承包',
                            area='起步区', workers=2100),
            BusinessLicense(id=8, name='雄安建工机电安装有限公司', cert_level='二级', cert_type='机电安装专业承包',
                            area='容东片区', workers=340),
        ]
        for b in businesses:
            db.session.add(b)
        print(f'[数据] 插入 {len(businesses)} 个建筑业企业')

        # 公交站点（10条）
        bus_stations = [
            TransportStation(id=1, name='雄安站东广场', lines='雄安1路/3路/K1线/旅游1线',
                             area='昝岗片区', daily_flow=18500, lng=116.160, lat=39.055),
            TransportStation(id=2, name='市民服务中心', lines='雄安1路/2路/5路/301路',
                             area='容东片区', daily_flow=12500, lng=116.090, lat=39.048),
            TransportStation(id=3, name='容东安置区北', lines='雄安2路/6路/203路',
                             area='容东片区', daily_flow=8700, lng=116.105, lat=39.052),
            TransportStation(id=4, name='启动区总部区', lines='雄安1路/3路/4路/6路/K2线',
                             area='启动区', daily_flow=6200, lng=116.102, lat=39.045),
            TransportStation(id=5, name='容城汽车站', lines='雄安1路/2路/城际801/城际803',
                             area='容城县城', daily_flow=9800, lng=116.072, lat=39.068),
            TransportStation(id=6, name='白洋淀站', lines='雄安5路/K1线/旅游1线/旅游2线',
                             area='白洋淀', daily_flow=15800, lng=116.068, lat=38.936),
            TransportStation(id=7, name='雄县汽车站', lines='雄安201路/202路/城际805',
                             area='雄县县城', daily_flow=7400, lng=116.120, lat=39.020),
            TransportStation(id=8, name='安新客运枢纽', lines='雄安301路/302路/旅游3线',
                             area='安新县城', daily_flow=6500, lng=116.032, lat=38.998),
            TransportStation(id=9, name='起步区科学园', lines='雄安4路/6路/206路',
                             area='起步区', daily_flow=4100, lng=116.112, lat=39.040),
            TransportStation(id=10, name='雄安站西广场', lines='雄安1路/3路/K1线',
                             area='昝岗片区', daily_flow=11200, lng=116.158, lat=39.054),
        ]
        for st in bus_stations:
            db.session.add(st)
        print(f'[数据] 插入 {len(bus_stations)} 个公交站点')

        # 河湖（6条）
        waters = [
            WaterBody(id=1, name='白洋淀', wtype='湖', area='白洋淀',
                      water_area=366.0, quality='III', level=6.8),
            WaterBody(id=2, name='赵王新河', wtype='河', area='起步区',
                      water_area=0, quality='III', level=5.2),
            WaterBody(id=3, name='府河', wtype='河', area='容城',
                      water_area=0, quality='IV', level=3.8),
            WaterBody(id=4, name='南拒马河', wtype='河', area='起步区',
                      water_area=0, quality='II', level=4.5),
            WaterBody(id=5, name='烧车淀', wtype='湖', area='白洋淀',
                      water_area=18.5, quality='III', level=7.1),
            WaterBody(id=6, name='大碱厂水库', wtype='水库', area='雄县',
                      water_area=2.8, quality='II', level=12.6),
        ]
        for w in waters:
            db.session.add(w)
        print(f'[数据] 插入 {len(waters)} 条河湖数据')

        # 市政设施（10条）
        munis = [
            MunicipalNode(id=1, name='启动区综合管廊A段', ftype='管廊', area='启动区',
                          status='正常', lng=116.105, lat=39.045),
            MunicipalNode(id=2, name='容东片区1号供热站', ftype='供热', area='容东片区',
                          status='正常', lng=116.098, lat=39.050),
            MunicipalNode(id=3, name='起步区EA1主干道路灯段', ftype='路灯', area='起步区',
                          status='正常', lng=116.125, lat=39.042),
            MunicipalNode(id=4, name='容西片区燃气管网调压站', ftype='燃气', area='容西片区',
                          status='正常', lng=116.078, lat=39.058),
            MunicipalNode(id=5, name='启动区DN800供水主管', ftype='供水', area='启动区',
                          status='正常', lng=116.110, lat=39.043),
            MunicipalNode(id=6, name='容东片区市政道路01号井盖', ftype='井盖', area='容东片区',
                          status='异常', lng=116.100, lat=39.047),
            MunicipalNode(id=7, name='白洋淀大道跨府河桥', ftype='桥梁', area='安新',
                          status='正常', lng=116.045, lat=38.978),
            MunicipalNode(id=8, name='启动区污水厂配套管网', ftype='排水', area='启动区',
                          status='正常', lng=116.115, lat=39.041),
            MunicipalNode(id=9, name='昝岗片区2号路灯段', ftype='路灯', area='昝岗片区',
                          status='正常', lng=116.162, lat=39.053),
            MunicipalNode(id=10, name='容城朝阳路1号井盖', ftype='井盖', area='容城县城',
                          status='正常', lng=116.070, lat=39.066),
        ]
        for m in munis:
            db.session.add(m)
        print(f'[数据] 插入 {len(munis)} 个市政设施')

        db.session.commit()
        print('\n[完成] 数据库初始化成功！')
        print('=' * 60)
        print('默认账号清单（18个用户，覆盖全部12个处室）：')
        print('  系统管理员  admin / admin123          (信息化处)')
        print('  局领导      zhangju / zhangju123      (局领导)')
        print('  处室负责人  chenzhuren / chenzhuren123 (办公室)')
        print('  处室负责人  liuchu / liuchu123         (政策法规处)')
        print('  处室负责人  yangchu / yangchu123       (政务服务处)')
        print('  处室负责人  zhouchu / zhouchu123       (城乡发展处)')
        print('  处室负责人  wuchu / wuchu123           (房屋管理处)')
        print('  处室负责人  lichu / lichu123           (工程质量安全处)')
        print('  处室负责人  zhengchu / zhengchu123     (建筑市场处)')
        print('  处室负责人  chuchu / chuchu123         (综合交通组)')
        print('  处室负责人  weichu / weichu123         (水利组)')
        print('  处室负责人  jiangchu / jiangchu123     (城市管理处)')
        print('  处室负责人  shenchu / shenchu123       (城市建设监察处)')
        print('  处室负责人  hanchu / hanchu123         (信息化处)')
        print('  业务经办人  wangjing / wangjing123     (城乡发展处)')
        print('  业务经办人  sunjing / sunjing123       (工程质量安全处)')
        print('  业务经办人  zhaojiaotong / zhaojiaotong123 (综合交通组)')
        print('  业务经办人  fengjing / fengjing123     (建筑市场处)')
        print('=' * 60)


if __name__ == '__main__':
    init_db()
