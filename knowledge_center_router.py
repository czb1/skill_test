from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Response, BackgroundTasks
from fastapi import Request

from exception.exceptions import ProjectException
from knowledge_center.skill_eval_center import get_skill_eval_results
from logger import logger
from service_resp import ResponseModel
from utils.login_utils import cookie_login_in
from configs_info.constants import UID
from services.knowledge_center_service import get_okf_project_id_service
from route.params.knowledge_center_models import ScopeWithScenarioModel, \
    ScopeWithScenarioPageModel, ProductKnowledgeAddKbModel, \
    ProductKnowledgeDeleteKbModel, ManagementGlobalInfoRequest, RuleContentRequest, CodeTreeRequest, \
    CodeSearchRequest, CodeManageModel, CodeQueryFilter, OkfBindRequest, ProductOwnerModel, \
    OkfRefreshRequest, \
    CodeSearchRequest, CodeManageModel, CodeQueryFilter, OkfBindRequest, \
    EvoTaskCountRequest, EvoTaskListRequest, EvoTaskInsertRequest, \
    EvoTaskUpdateSpecRequest, EvoTaskDeleteRequest, EvoTaskUpdateRequest, \
    EvalTaskCreateRequest, EvalTaskListRequest, \
    EvalCallbackRequest, ReflowCallbackRequest, \
    SkillEvaluableListRequest, SkillEvalTaskCreateRequest, SkillEvalBatchListRequest, \
    FollowProductRequest
from services.knowledge_center_service import get_management_global_info, get_kb_global_info, \
    get_kb_list, add_product_kb_relation, delete_product_kb_relation, \
    get_code_status_new, get_code_list_new, get_rule_status_new, get_rule_list_new, get_rule_content, \
    get_skill_status, get_skill_list, get_operating_status, get_operating_list, get_code_tree, \
    get_code_search, update_repo_manage_info, search_user, update_product_owner, \
    list_okf, bind_okf, get_okf, delete_okf, \
    list_okf_files, read_okf_file, read_okf_config, read_okf_log, \
    get_center_knowledge_nums, refresh_okf, \
    get_code_search, update_repo_manage_info, \
    get_evo_task_count, get_evo_task_list, \
    insert_evo_task, insert_evo_task_background, update_spec_diff, get_evo_task_by_id, \
    delete_evo_task, update_evo_task_fields, get_all_product_kb_ids, get_management_hierarchy, create_eval_task, \
    get_eval_task_list, get_eval_task_detail, get_eval_task_reflow, mark_eval_reflow_done, reject_eval_reflow, \
    delete_eval_task, get_eval_summary, handle_eval_only_callback, get_followed_products, follow_product, \
    unfollow_product, get_eval_overview_stats, get_knowledge_consume_stats, handle_reflow_only_callback, \
    get_offering_ids_by_product_name, get_okf_infos, list_okf_repo_tree, read_okf_repo_file, \
    get_evaluable_skills, get_skill_eval_modes, create_skill_eval_batch, \
    get_skill_eval_batch_list, get_skill_eval_batch_detail

knowledge_center_route = APIRouter(prefix="/knowledgeCenter")


def _get_uid_from_request(request: Request):
    """从请求 cookie 中解析当前登录用户工号（uid）。
    无 cookie 或解析失败时返回 None，不抛异常（creator 允许为空）。"""
    cookie = request.headers.get("cookie")
    if not cookie:
        return None
    try:
        user_info = cookie_login_in(cookie)
        return user_info.get(UID) if user_info else None
    except Exception as e:
        logger.warning(f"从 cookie 解析用户工号失败: {e}")
        return None


######################## 产业知识库 ########################

@knowledge_center_route.post("/productKnowledge/GlobalInfo")
def query_prod_knowledge_global_info(req: ScopeWithScenarioModel):
    """查询指定产品的产品知识总览数据"""
    try:
        data = get_kb_global_info(offering_id=req.offering_id, pdu=req.pdu, department=req.department)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/productKnowledge/kb_list")
def query_prod_knowledge_kb_list(req: ScopeWithScenarioPageModel):
    """查询指定产品的知识库列表（分页）"""
    try:
        data = get_kb_list(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                           page=req.page, page_size=req.page_size)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/productKnowledge/add_kb")
def add_product_kb(req: ProductKnowledgeAddKbModel):
    """新增产品与知识库的关联"""
    if not req.offering_id or not req.kb_id or not req.kb_url:
        raise HTTPException(status_code=400, detail="offering_id/kb_id/kb_url is all required")
    try:
        add_product_kb_relation(offering_id=req.offering_id, kb_url=req.kb_url, kb_id=req.kb_id)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/productKnowledge/delete_kb")
def delete_product_kb(req: ProductKnowledgeDeleteKbModel):
    """解除产品与知识库的关联"""
    if not req.offering_id or not req.kb_id:
        raise HTTPException(status_code=400, detail="offering_id/kb_id is required")
    try:
        delete_product_kb_relation(offering_id=req.offering_id, kb_id=req.kb_id)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/productKnowledge/product_kb_ids")
def query_all_product_kb_ids():
    """查询全部产品及其关联知识库id集合（按 product_name 分组，v 为 kb_id 列表）"""
    try:
        data = get_all_product_kb_ids()
        return ResponseModel.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## 管理首页 ########################

@knowledge_center_route.post("/management/global_info")
def management_global_info(req: ManagementGlobalInfoRequest):
    """管理首页：全量统计 + 环节统计 + 层级树"""
    try:
        data = get_management_global_info(scenario=req.scenario, hierarchy_only=req.hierarchy)
        return ResponseModel.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/management/consumeStats")
def management_consume_stats(req: ManagementGlobalInfoRequest):
    """管理首页：知识消费统计（累计消费总次数 / 消费满足度）—— 调用 bicloud 接口"""
    try:
        data = get_knowledge_consume_stats(offering_id=req.offering_id, pdu=req.pdu, department=req.department)
        return ResponseModel.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/management/hierarchy")
def management_hierarchy():
    """管理首页：仅返回层级结构树（pdu→department→product），不做统计"""
    try:
        data = get_management_hierarchy()
        return ResponseModel.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## 产品责任人 ########################

@knowledge_center_route.get("/user/search")
def user_search(info: str = Query(..., min_length=1, max_length=128, description="姓名或工号关键字")):
    """按姓名/工号关键字搜索责任人（代理 fuyao hw-userinfo）"""
    try:
        data = search_user(info)
        return ResponseModel.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/product/owner")
def product_owner(req: ProductOwnerModel):
    """更新产品责任人；owner_name/owner_id 传 null 表示清空"""
    if not req.offering_id:
        raise HTTPException(status_code=400, detail="offering_id is required")
    try:
        data = update_product_owner(offering_id=req.offering_id,
                                    owner_name=req.owner_name, owner_id=req.owner_id)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## 代码仓 ########################

@knowledge_center_route.post("/code/status")
def code_status(req: ScopeWithScenarioModel):
    """代码仓数量"""
    try:
        data = get_code_status_new(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                                   scenario=req.scenario)
        return ResponseModel.success(data=data, meta_data={"scenario": req.scenario})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/list")
def code_list(req: CodeTreeRequest):
    """代码仓列表（树形懒加载）"""
    try:
        data = get_code_tree(CodeQueryFilter(**req.model_dump()))
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/search")
def code_search(req: CodeSearchRequest):
    """代码仓路径搜索（扁平列表，按字母表排序）"""
    try:
        data = get_code_search(CodeQueryFilter(**req.model_dump()))
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/manage")
def code_manage(req: CodeManageModel):
    """更新指定代码仓的管理状态、DDL时间、优先级、负责人。
    仅更新请求中实际传入的字段；显式传 null 表示清空该字段。"""
    try:
        update_fields = req.model_dump(exclude_unset=True, exclude={"repo_url"})
        updated_count = update_repo_manage_info(req.repo_url, update_fields)
        return ResponseModel.success(data={"updated_count": updated_count})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## 规范 ########################

@knowledge_center_route.post("/rule/status")
def rule_status(req: ScopeWithScenarioModel):
    """规范数量"""
    try:
        data = get_rule_status_new(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                                   scenario=req.scenario)
        return ResponseModel.success(data=data, meta_data={"scenario": req.scenario})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/rule/list")
def rule_list(req: ScopeWithScenarioModel):
    """规范路径列表（不分页）"""
    try:
        data = get_rule_list_new(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                                 scenario=req.scenario)
        return ResponseModel.success(data=data, meta_data={"scenario": req.scenario})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/rule/content")
def rule_content(req: RuleContentRequest):
    """规范正文（复用现有接口）"""
    data = get_rule_content(req.file_path)
    return ResponseModel.success(data=data)


######################## Skill ########################

@knowledge_center_route.post("/skill/status")
def skill_status(req: ScopeWithScenarioModel):
    """Skill数量"""
    try:
        data = get_skill_status(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                                scenario=req.scenario)
        return ResponseModel.success(data=data, meta_data={"scenario": req.scenario})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/skill/list")
def skill_list(req: ScopeWithScenarioPageModel):
    """Skill列表（分页）"""
    try:
        data = get_skill_list(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                              scenario=req.scenario, page=req.page, page_size=req.page_size)
        return ResponseModel.success(data=data, meta_data={"scenario": req.scenario})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## Skill 评测 ########################
@knowledge_center_route.get("/skillEval/modes")
def skill_eval_modes():
    try:
        return ResponseModel.success(data=get_skill_eval_modes())
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@knowledge_center_route.post("/skillEval/evaluableSkills")
def skill_eval_evaluable_list(req: SkillEvaluableListRequest):
    """用于勾选触发评测：仅显示状态为已完成的 Skill。"""
    try:
        data = get_evaluable_skills(
            offering_id=req.offering_id, pdu=req.pdu, department=req.department,
            keyword=req.keyword, page=req.page, page_size=req.page_size)
        return ResponseModel.success(data=data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


class SkillEvalResultsRequest(SkillEvaluableListRequest):
    # 默认保留原有完整响应；列表先查询状态，再按当前页 ID 加载报告。
    include_reports: bool = True
    skill_ids: Optional[List[str]] = None


@knowledge_center_route.post("/skillEval/results")
def skill_eval_results(req: SkillEvalResultsRequest):
    """include_reports=false 只返回状态；skill_ids 限定需要读取报告的 Skill。"""
    try:
        data = get_skill_eval_results(
            offering_id=req.offering_id, pdu=req.pdu, department=req.department,
            keyword=req.keyword, page=req.page, page_size=req.page_size,
            include_reports=req.include_reports, skill_ids=req.skill_ids)
        return ResponseModel.success(data=data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@knowledge_center_route.post("/skillEval/taskCreate")
def skill_eval_task_create(req: SkillEvalTaskCreateRequest):
    """直接提交外部服务；按 Skill 返回各维度提交结果，不生成本地批次。"""
    try:
        data = create_skill_eval_batch(
            skill_ids=req.skill_ids, modes=req.modes,
            offering_id=req.offering_id, pdu=req.pdu, department=req.department,
            batch_name=req.batch_name, creator=req.creator or "system",
            model=req.model, agent=req.agent, description=req.description)
        return ResponseModel.success(data=data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@knowledge_center_route.post("/skillEval/batchList")
def skill_eval_batch_list(req: SkillEvalBatchListRequest):
    """旧路径过渡兼容：返回值已改为 Skill 粒度，推荐改调 /results。"""
    try:
        data = get_skill_eval_batch_list(
            dept_name=req.dept_name, product_id=req.product_id, pdu_name=req.pdu_name,
            status=req.status, keyword=req.keyword, creator=req.creator,
            page=req.page, page_size=req.page_size)
        return ResponseModel.success(data=data)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))


@knowledge_center_route.get("/skillEval/batchDetail")
def skill_eval_batch_detail(batch_id: str = Query(..., description="已停用的批次ID")):
    raise HTTPException(status_code=410, detail="已取消批次详情，请改调 /skillEval/results")



######################## 作业系统 ########################

@knowledge_center_route.post("/operating/status")
def operating_status(req: ScopeWithScenarioModel):
    """作业系统数量"""
    try:
        data = get_operating_status(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                                    scenario=req.scenario)
        return ResponseModel.success(data=data, meta_data={"scenario": req.scenario})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/operating/list")
def operating_list(req: ScopeWithScenarioPageModel):
    """作业系统列表（分页）"""
    try:
        data = get_operating_list(offering_id=req.offering_id, pdu=req.pdu, department=req.department,
                                  scenario=req.scenario, page=req.page, page_size=req.page_size)
        return ResponseModel.success(data=data, meta_data={"scenario": req.scenario})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## OKF 管理 ########################

@knowledge_center_route.get("/okf/list")
def okf_list(offering_id: str = Query(..., description="产品 Offering ID")):
    """查询 Offering 关联的 OKF 列表"""
    try:
        data = list_okf(offering_id)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/okf")
def okf_bind(req: OkfBindRequest):
    """绑定 OKF 代码仓"""
    if not req.offering_id or not req.repo_url or not req.branch:
        raise HTTPException(status_code=400, detail="offering_id/repo_url/branch is all required")
    try:
        data = bind_okf(req.offering_id, req.repo_url, req.branch)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/project_id")
def okf_project_id(offering_id: str = Query(..., description="产品 Offering ID")):
    """查询 Offering 关联的 OKF 的 project_id"""
    try:
        project_id, branch = get_okf_project_id_service(offering_id)
        return ResponseModel.success(data={"project_id": project_id, "branch": branch})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/product/offering_id")
def product_offering_id(product_name: str = Query(..., description="产品名称")):
    """按产品名称精确查询 offering_id 列表。"""
    try:
        return ResponseModel.success(
            data=get_offering_ids_by_product_name(product_name)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/infos")
def okf_infos(status: str = Query("all", description="OKF状态，默认 all 返回全部")):
    """查询已归档 OKF 信息（产品名、offering_id、repo_url、branch）。"""
    try:
        return ResponseModel.success(data=get_okf_infos(status))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/repo/tree")
def okf_repo_tree(response: Response,
                  project_id: str = Query(..., description="CodeHub 项目 ID"),
                  branch: str = Query(..., description="分支"),
                  root: str = Query("", description="起始路径，默认根目录"),
                  page: int = Query(1, ge=1),
                  per_page: int = Query(100, ge=1, le=100)):
    """代理 CodeHub tree 接口，token 只保留在服务端。"""
    try:
        items, total_pages = list_okf_repo_tree(project_id, branch, root, page, per_page)
        response.headers["X-Total-Pages"] = str(total_pages or 1)
        return ResponseModel.success(data=items)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/repo/raw")
def okf_repo_raw(project_id: str = Query(..., description="CodeHub 项目 ID"),
                 branch: str = Query(..., description="分支"),
                 path: str = Query(..., description="文件路径")):
    """代理 CodeHub raw 接口，token 只保留在服务端。"""
    try:
        content = read_okf_repo_file(project_id, branch, path)
        return Response(content=content, media_type="application/octet-stream")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/{okf_id}")
def okf_detail(okf_id: str):
    """查询 OKF 详情 / 状态"""
    try:
        data = get_okf(okf_id)
        if data is None:
            raise HTTPException(status_code=404, detail=f"OKF {okf_id} not found")
        return ResponseModel.success(data=data)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.delete("/okf/{okf_id}")
def okf_delete(okf_id: str):
    """删除 OKF"""
    try:
        success = delete_okf(okf_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"OKF {okf_id} not found")
        return ResponseModel.success(data={"success": True})
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/{okf_id}/files")
def okf_files(okf_id: str, path: str = Query(".", description="相对于 Git 仓库根的路径")):
    """浏览 OKF 目录"""
    try:
        data = list_okf_files(okf_id, path)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/{okf_id}/files/content")
def okf_file_content(okf_id: str, path: str = Query(..., description="相对于 Git 仓库根的文件路径")):
    """读取 OKF 文件内容"""
    try:
        data = read_okf_file(okf_id, path)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/{okf_id}/config")
def okf_config(okf_id: str):
    """读取 OKF 配置 (okf-config.yaml)"""
    try:
        data = read_okf_config(okf_id)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/okf/{okf_id}/log")
def okf_log(okf_id: str):
    """读取 OKF 日志 (log.md)"""
    try:
        data = read_okf_log(okf_id)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/okf/refresh")
def okf_refresh(req: OkfRefreshRequest):
    """按产品粒度刷新中心仓知识：整仓重新 clone → 重统计 → 落库。
    手动更新按钮 / 外部 24:00 兜底任务共用；refreshing 状态机防重。"""
    try:
        data = refresh_okf(req.offering_id)
        return ResponseModel.success(data=data)
    except ProjectException:
        raise
    except ValueError as e:
        raise ProjectException(ProjectException.PARAM_VALID_ERROR,
                               content=str(e))
    except Exception:
        logger.exception("刷新中心仓知识失败")
        raise ProjectException(ProjectException.OTHER_ERROR,
                               content="内部服务异常")


@knowledge_center_route.post("/okf/center_knowledge")
def okf_center_knowledge(req: ScopeWithScenarioModel):
    """按范围查询中心仓知识数（产品/开发部/PDU 绑定代码仓 .raw 目录下递归统计的文件总数）"""
    try:
        data = get_center_knowledge_nums(offering_id=req.offering_id,
                                         pdu=req.pdu,
                                         department=req.department)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ProjectException:
        raise
    except Exception:
        logger.exception("查询中心仓知识数失败")
        raise HTTPException(status_code=500, detail="内部服务异常")


######################## Spec 自进化任务 ########################

@knowledge_center_route.post("/code/evoTaskCount")
def evo_task_count(req: EvoTaskCountRequest):
    """获取代码仓自进化任务总数量（合并待处理与已处理）"""
    try:
        data = get_evo_task_count(req.repo_url)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/evoTaskList")
def evo_task_list(req: EvoTaskListRequest):
    """获取代码仓自进化任务列表（不区分状态，返回全部）"""
    try:
        data = get_evo_task_list(req.repo_url, req.status)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/evoTaskInsert")
def evo_task_insert(req: EvoTaskInsertRequest, background_tasks: BackgroundTasks):
    """自进化任务入库并自动接受：立即返回，后台异步调用 mr_server 创建 MR"""
    try:
        task_id = insert_evo_task(req.repo_url, req.mr_url, req.spec_diff,
                                  req.baseline_report, req.verify_report,
                                  req.improvement_overview, req.delta_metric)
        # 查询任务信息用于后台处理
        task = get_evo_task_by_id(task_id)
        background_tasks.add_task(insert_evo_task_background, task_id, task)
        return ResponseModel.success(data={"task_id": task_id})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/evoTaskUpdateSpec")
def evo_task_update_spec(req: EvoTaskUpdateSpecRequest):
    """更新自进化任务的 spec 内容（编辑后保存）"""
    try:
        update_spec_diff(req.task_id, req.new_spec_content)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/evoTaskDelete")
def evo_task_delete(req: EvoTaskDeleteRequest):
    """逻辑删除自进化任务"""
    try:
        delete_evo_task(req.task_id)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/code/evoTaskUpdate")
def evo_task_update(req: EvoTaskUpdateRequest):
    """更新自进化任务字段，仅修改传入的字段，未传入的字段保持不变"""
    try:
        fields = req.model_dump(exclude={"id"}, exclude_none=True)
        if not fields:
            raise ValueError("至少需要传入一个待修改字段")
        update_evo_task_fields(req.id, fields)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## 知识评测与回流 ########################

@knowledge_center_route.post("/eval/taskCreate")
def eval_task_create(req: EvalTaskCreateRequest, request: Request):
    """新建评测任务，异步触发 mock 评测"""
    try:
        # creator 为空时，从请求 cookie 中解析当前登录用户工号自动填充；
        # 无 cookie 或解析失败时兜底为 "system"
        creator = req.creator
        if not creator:
            creator = _get_uid_from_request(request) or "system"
            logger.info(f"creator 未传入，自动填充: creator={creator}")

        data = create_eval_task(
            task_type=req.task_type,
            trigger_mode=req.trigger_mode,
            task_name=req.task_name,
            task_source=req.task_source,
            modes=req.modes,
            dept_name=req.dept_name,
            product_id=req.product_id,
            pdu_name=req.pdu_name,
            creator=creator,
            reflow_expect=req.reflow_expect,
            trigger_source=req.trigger_source,
            operations_url=req.operations_url,
            target_repo=req.target_repo,
            target_repo_ref=req.target_repo_ref,
            has_reflow=req.has_reflow or 0,
        )
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/eval/taskList")
def eval_task_list(req: EvalTaskListRequest):
    """评测任务列表（支持 dept_name/product_id/pdu_name/status/reflow_status/keyword/creator 过滤 + 分页）"""
    try:
        data = get_eval_task_list(
            dept_name=req.dept_name, product_id=req.product_id, pdu_name=req.pdu_name,
            status=req.status, reflow_status=req.reflow_status, keyword=req.keyword,
            creator=req.creator, page=req.page, page_size=req.page_size)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/eval/taskDetail")
def eval_task_detail(task_id: str = Query(..., description="评测任务ID")):
    """评测任务详情（主表 + metrics）"""
    try:
        data = get_eval_task_detail(task_id)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/eval/taskReflow")
def eval_task_reflow(task_id: str = Query(..., description="评测任务ID")):
    """评测任务回流详情（effect_compare + suggestions + reflow_mr）"""
    try:
        data = get_eval_task_reflow(task_id)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/eval/reflowDone")
def eval_reflow_done(task_id: str = Query(..., description="评测任务ID")):
    """标记回流完成"""
    try:
        mark_eval_reflow_done(task_id)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/eval/reflowReject")
def eval_reflow_reject(task_id: str = Query(..., description="评测任务ID")):
    """拒绝回流"""
    try:
        reject_eval_reflow(task_id)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/eval/summary")
def eval_summary(dept_name: str = Query(None, description="部门名称"),
                 product_id: str = Query(None, description="产品ID"),
                 pdu_name: str = Query(None, description="PDU名称")):
    """评测任务汇总（design/develop/test 三阶段统计）"""
    try:
        data = get_eval_summary(dept_name=dept_name, product_id=product_id, pdu_name=pdu_name)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.get("/eval/overviewStats")
def eval_overview_stats(dept_name: str = Query(None, description="部门名称"),
                        product_id: str = Query(None, description="产品ID"),
                        pdu_name: str = Query(None, description="PDU名称")):
    """知识全景页面 - 评测回流四指标统计
    返回: eval_task_count / coverage_gain_pct / verify_passed / verify_failed / reflow_by_type
    """
    try:
        data = get_eval_overview_stats(dept_name=dept_name, product_id=product_id, pdu_name=pdu_name)
        return ResponseModel.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


######################## 用户关注产品 ########################

@knowledge_center_route.get("/follow/products")
def get_follow_products(request: Request, user_id: str = Query(None, description="用户ID")):
    """查询用户关注的产品列表。
    权限：从 cookie 解析当前登录用户工号，解析失败返回 401；
    以 cookie 中的 user_id 为准（忽略请求传入的 user_id，防止越权查询他人关注列表）。"""
    cookie_uid = _get_uid_from_request(request)
    if not cookie_uid:
        raise HTTPException(status_code=401, detail="未登录或 cookie 失效，无法获取用户身份")
    try:
        data = get_followed_products(user_id=cookie_uid)
        return ResponseModel.success(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/follow/product")
def follow_product_api(req: FollowProductRequest, request: Request):
    """关注产品/部门。
    权限：从 cookie 解析当前登录用户工号，解析失败返回 401；
    以 cookie 中的 user_id 为准（忽略 req.user_id，防止越权替他人关注）。"""
    cookie_uid = _get_uid_from_request(request)
    if not cookie_uid:
        raise HTTPException(status_code=401, detail="未登录或 cookie 失效，无法获取用户身份")
    try:
        data = follow_product(
            user_id=cookie_uid, follow_type=req.follow_type,
            offering_id=req.offering_id,
            pdu=req.pdu, department=req.department, product_name=req.product_name)
        return ResponseModel.success(data=data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.delete("/follow/product")
def unfollow_product_api(request: Request,
                         follow_type: str = Query("product", description="关注类型: product/department/pdu"),
                         offering_id: str = Query(None, description="产品ID"),
                         department: str = Query(None, description="开发部名称"),
                         pdu: str = Query(None, description="PDU名称")):
    """取消关注产品/部门/PDU。
    权限：从 cookie 解析当前登录用户工号，解析失败返回 401；
    以 cookie 中的 user_id 为准（防止越权取消他人关注）。"""
    cookie_uid = _get_uid_from_request(request)
    if not cookie_uid:
        raise HTTPException(status_code=401, detail="未登录或 cookie 失效，无法获取用户身份")
    try:
        unfollow_product(user_id=cookie_uid, follow_type=follow_type,
                         offering_id=offering_id, department=department, pdu=pdu)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.delete("/eval/taskDelete")
def eval_task_delete(task_id: str = Query(..., description="评测任务ID")):
    """逻辑删除评测任务"""
    try:
        delete_eval_task(task_id)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/eval/evalCallback")
def eval_callback(req: EvalCallbackRequest):
    """评测结果回写接口（第一次回调：仅 eval）。
    更新主表 status/eval_duration + metrics 子表，不碰回流数据。
    """
    try:
        handle_eval_only_callback(req)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@knowledge_center_route.post("/eval/reflowCallback")
def reflow_callback(req: ReflowCallbackRequest):
    """回流结果回写接口（第二次回调：仅 reflow）。
    更新主表 reflow_status/reflow_expect/reflow_mr/effect_compare + suggestions 子表，不碰评测数据。
    """
    try:
        handle_reflow_only_callback(req)
        return ResponseModel.success()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

