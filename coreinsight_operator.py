    # ── Skill 评测 ────────────────────────────────────────────
    def query_skill_eval_result_skills(self, offering_ids, keyword=None,
                                       page=1, page_size=10):
        """范围内开发已完成的 Skill；在统计总数和分页前过滤目录状态。"""
        page = max(int(page), 1)
        page_size = min(max(int(page_size), 1), 100)
        if not offering_ids:
            return {"total": 0, "page": page, "page_size": page_size,
                    "pages": 0, "items": []}
        with self.connector.session_context() as session:
            try:
                skill_ids_q = session.query(TKmProductSkillRelation.skill_id).filter(
                    TKmProductSkillRelation.offering_id.in_(offering_ids)
                ).distinct().subquery()
                base_q = session.query(TKmSkillInfos).filter(
                    TKmSkillInfos.id.in_(session.query(skill_ids_q.c.skill_id)),
                    TKmSkillInfos.status == "已完成",
                )
                if keyword:
                    like = f"%{keyword}%"
                    base_q = base_q.filter(or_(
                        TKmSkillInfos.skill_name.like(like),
                        TKmSkillInfos.skill_description.like(like)))
                total = base_q.count()
                rows = base_q.order_by(TKmSkillInfos.skill_name, TKmSkillInfos.id).offset(
                    (page - 1) * page_size).limit(page_size).all()
                items = []
                for row in rows:
                    item = row.to_dict()
                    # 归属匹配必须使用存储的实际名称，不能用显示名或自行删除版本后缀。
                    item["skill_id"] = row.id
                    item["skill_name"] = row.skill_name
                    item["name"] = row.skill_name
                    item["skill_status"] = item.get("status")
                    items.append(item)
                rel_map = {}
                if items:
                    relations = session.query(
                        TKmProductSkillRelation.skill_id,
                        TKmProductSkillRelation.offering_id,
                    ).filter(
                        TKmProductSkillRelation.skill_id.in_([it["skill_id"] for it in items]),
                        TKmProductSkillRelation.offering_id.in_(offering_ids),
                    ).distinct().all()
                    for skill_id, offering_id in relations:
                        rel_map.setdefault(skill_id, []).append(offering_id)
                for item in items:
                    item["offering_ids"] = rel_map.get(item["skill_id"], [])
                return {"total": total, "page": page, "page_size": page_size,
                        "pages": (total + page_size - 1) // page_size, "items": items}
            except SQLAlchemyError as error:
                logger.error(f"查询部门 Skill 评测目录失败: {error}")
                raise

    def query_skill_eval_name_owners(self, skill_names):
        """全库检查名称对应哪些 Skill ID；跨部门重名也不能误关联。"""
        names = list(dict.fromkeys(name for name in skill_names if name))
        if not names:
            return {}
        with self.connector.session_context() as session:
            try:
                rows = session.query(TKmSkillInfos.skill_name, TKmSkillInfos.id).filter(
                    TKmSkillInfos.skill_name.in_(names)).distinct().all()
                owners = {}
                for name, skill_id in rows:
                    owners.setdefault(name, []).append(skill_id)
                return owners
            except SQLAlchemyError as error:
                logger.error(f"检查 Skill 评测名称归属失败: {error}")
                raise

    def query_evaluable_skills(self, offering_ids: List[str], keyword: str = None,
                               page: int = 1, page_size: int = 10):
        """查询范围内可评测的 Skill：仅要求状态为已完成。
        包地址/版本号缺失时，在创建评测任务时从 harness 接口实时解析。"""
        if not offering_ids:
            return {"total": 0, "page": page, "page_size": page_size, "pages": 0, "items": []}
        with self.connector.session_context() as session:
            try:
                skill_ids_q = session.query(TKmProductSkillRelation.skill_id).filter(
                    TKmProductSkillRelation.offering_id.in_(offering_ids)
                ).distinct().subquery()

                base_q = session.query(TKmSkillInfos).filter(
                    TKmSkillInfos.id.in_(session.query(skill_ids_q.c.skill_id)),
                    TKmSkillInfos.status == "已完成",
                )
                if keyword:
                    like = f"%{keyword}%"
                    base_q = base_q.filter(or_(
                        TKmSkillInfos.skill_name.like(like),
                        TKmSkillInfos.skill_description.like(like),
                    ))

                total = base_q.count()
                if page < 1:
                    page = 1
                page_size = min(max(page_size, 1), 100)
                rows = base_q.order_by(
                    TKmSkillInfos.skill_name, TKmSkillInfos.id
                ).offset((page - 1) * page_size).limit(page_size).all()
                items = [r.to_dict() for r in rows]

                # 附带 Skill 命中的产品范围，便于前端展示/核对
                if items:
                    skill_ids = [it["skill_id"] for it in items]
                    rel_rows = session.query(
                        TKmProductSkillRelation.skill_id,
                        TKmProductSkillRelation.offering_id,
                    ).filter(
                        TKmProductSkillRelation.skill_id.in_(skill_ids),
                        TKmProductSkillRelation.offering_id.in_(offering_ids),
                    ).distinct().all()
                    rel_map = {}
                    for skill_id, offering_id in rel_rows:
                        rel_map.setdefault(skill_id, []).append(offering_id)
                    for it in items:
                        it["offering_ids"] = rel_map.get(it["skill_id"], [])

                pages = (total + page_size - 1) // page_size if total > 0 else 0
                return {"total": total, "page": page, "page_size": page_size,
                        "pages": pages, "items": items}
            except SQLAlchemyError as e:
                logger.error(f"查询可评测Skill失败: {str(e)}")
                raise

    def query_skill_scope_products(self, skill_ids: List[str], offering_ids: List[str]) -> dict:
        """查询 Skill 在给定范围内命中的产品：{skill_id: [offering_id]}。"""
        if not skill_ids or not offering_ids:
            return {}
        with self.connector.session_context() as session:
            try:
                rows = session.query(
                    TKmProductSkillRelation.skill_id,
                    TKmProductSkillRelation.offering_id,
                ).filter(
                    TKmProductSkillRelation.skill_id.in_(skill_ids),
                    TKmProductSkillRelation.offering_id.in_(offering_ids),
                ).distinct().all()
                result = {}
                for skill_id, offering_id in rows:
                    result.setdefault(skill_id, []).append(offering_id)
                return result
            except SQLAlchemyError as e:
                logger.error(f"查询Skill范围产品失败: {str(e)}")
                raise

    def query_skill_infos_by_ids(self, skill_ids: List[str]) -> dict:
        """按 ID 批量查询 Skill 信息：{skill_id: dict}。"""
        if not skill_ids:
            return {}
        with self.connector.session_context() as session:
            try:
                rows = session.query(TKmSkillInfos).filter(
                    TKmSkillInfos.id.in_(skill_ids)
                ).all()
                return {r.id: r.to_dict() for r in rows}
            except SQLAlchemyError as e:
                logger.error(f"批量查询Skill信息失败: {str(e)}")
                raise

    def update_skill_package_info(self, skill_id: str, skill_package_url: str,
                                  version: str) -> None:
        """回填 Skill 包地址与版本号（从 harness 解析成功后调用）。"""
        with self.connector.session_context() as session:
            try:
                skill = session.query(TKmSkillInfos).filter(
                    TKmSkillInfos.id == skill_id).first()
                if not skill:
                    return
                skill.skill_package_url = skill_package_url
                skill.version = version
                session.commit()
            except SQLAlchemyError as e:
                logger.error(f"回填Skill包信息失败: skill_id={skill_id}, error={e}")
                raise

    def insert_skill_eval_batch(self, batch_name: str, creator: str,
                                modes: list, dept_name: str = None,
                                product_id: str = None, pdu_name: str = None,
                                total_count: int = 0, model: str = None,
                                agent: str = None, description: str = None) -> str:
        """插入 Skill 评测批次，返回批次 ID。"""
        batch_id = str(uuid.uuid4())
        with self.connector.session_context() as session:
            try:
                session.add(TSkillEvalBatch(
                    id=batch_id,
                    batch_name=batch_name,
                    dept_name=dept_name,
                    product_id=product_id,
                    pdu_name=pdu_name,
                    modes=modes,
                    model=model,
                    agent=agent,
                    description=description,
                    creator=creator,
                    status="processing",
                    total_count=total_count,
                    completed_count=0,
                    failed_count=0,
                    is_deleted=0,
                ))
                session.commit()
                return batch_id
            except SQLAlchemyError as e:
                logger.error(f"插入Skill评测批次失败: {e}")
                raise

    def insert_skill_eval_tasks(self, batch_id: str, tasks: List[dict]) -> List[str]:
        """批量插入 Skill 评测任务及产品关联，返回任务 ID 列表。
        tasks 元素: {skill_id, skill_name, skill_package_url, version, mode, offering_ids}"""
        task_ids = []
        with self.connector.session_context() as session:
            try:
                for item in tasks:
                    task_id = str(uuid.uuid4())
                    task_ids.append(task_id)
                    session.add(TSkillEvalTask(
                        id=task_id,
                        batch_id=batch_id,
                        skill_id=item["skill_id"],
                        skill_name=item.get("skill_name"),
                        skill_package_url=item.get("skill_package_url"),
                        version=item.get("version"),
                        mode=item["mode"],
                        status="pending",
                        updated_at=datetime.now(),
                    ))
                    for offering_id in item.get("offering_ids") or []:
                        session.add(TSkillEvalTaskProduct(
                            id=str(uuid.uuid4()),
                            task_id=task_id,
                            offering_id=offering_id,
                        ))
                session.commit()
                return task_ids
            except SQLAlchemyError as e:
                logger.error(f"批量插入Skill评测任务失败: {e}")
                raise

    def query_skill_eval_batch_list(self, dept_name: str = None, product_id: str = None,
                                    pdu_name: str = None, status: str = None,
                                    keyword: str = None, creator: str = None,
                                    page: int = 1, page_size: int = 10) -> dict:
        """Skill 评测批次列表（分页）。"""
        with self.connector.session_context() as session:
            try:
                query = session.query(TSkillEvalBatch).filter(
                    TSkillEvalBatch.is_deleted == 0)
                if dept_name:
                    query = query.filter(TSkillEvalBatch.dept_name == dept_name)
                if product_id:
                    query = query.filter(TSkillEvalBatch.product_id == product_id)
                if pdu_name:
                    query = query.filter(TSkillEvalBatch.pdu_name == pdu_name)
                if status:
                    query = query.filter(TSkillEvalBatch.status == status)
                if keyword:
                    query = query.filter(TSkillEvalBatch.batch_name.like(f"%{keyword}%"))
                if creator:
                    query = query.filter(TSkillEvalBatch.creator.like(f"%{creator}%"))
                total = query.count()
                if page < 1:
                    page = 1
                page_size = min(max(page_size, 1), 100)
                rows = query.order_by(
                    TSkillEvalBatch.created_at.desc(), TSkillEvalBatch.id.desc()
                ).offset((page - 1) * page_size).limit(page_size).all()
                return {"total": total, "list": [r.to_dict() for r in rows]}
            except SQLAlchemyError as e:
                logger.error(f"查询Skill评测批次列表失败: {e}")
                raise

    def query_skill_eval_batch_by_id(self, batch_id: str) -> dict:
        """查询单个 Skill 评测批次。"""
        with self.connector.session_context() as session:
            try:
                batch = session.query(TSkillEvalBatch).filter(
                    TSkillEvalBatch.id == batch_id,
                    TSkillEvalBatch.is_deleted == 0,
                ).first()
                if not batch:
                    raise ValueError(f"Skill评测批次 {batch_id} 不存在")
                return batch.to_dict()
            except SQLAlchemyError as e:
                logger.error(f"查询Skill评测批次失败: {e}")
                raise

    def query_skill_eval_tasks_by_batch(self, batch_id: str) -> list:
        """查询批次下所有 Skill 评测任务。"""
        with self.connector.session_context() as session:
            try:
                rows = session.query(TSkillEvalTask).filter(
                    TSkillEvalTask.batch_id == batch_id
                ).order_by(TSkillEvalTask.skill_name, TSkillEvalTask.mode).all()
                return [r.to_dict() for r in rows]
            except SQLAlchemyError as e:
                logger.error(f"查询Skill评测任务失败: {e}")
                raise

    def update_skill_eval_task(self, task_id: str, status: str = None,
                               external_task_id: str = None, report=None,
                               error: str = None) -> None:
        """更新 Skill 评测任务；仅更新传入的字段。"""
        with self.connector.session_context() as session:
            try:
                task = session.query(TSkillEvalTask).filter(
                    TSkillEvalTask.id == task_id).first()
                if not task:
                    raise ValueError(f"Skill评测任务 {task_id} 不存在")
                if status is not None:
                    task.status = status
                if external_task_id is not None:
                    task.external_task_id = external_task_id
                if report is not None:
                    task.report = report
                if error is not None:
                    task.error = error
                task.updated_at = datetime.now()
                session.commit()
            except SQLAlchemyError as e:
                logger.error(f"更新Skill评测任务失败: {e}")
                raise

    def query_skill_eval_tasks_for_polling(self, limit: int = 20) -> list:
        """查询需要 worker 处理的任务：待提交，或已提交但未拿到终态/报告。"""
        with self.connector.session_context() as session:
            try:
                query = session.query(TSkillEvalTask).filter(or_(
                    TSkillEvalTask.status == "pending",
                    (TSkillEvalTask.external_task_id.isnot(None)) & or_(
                        ~TSkillEvalTask.status.in_(["completed", "failed"]),
                        (TSkillEvalTask.status == "completed") & TSkillEvalTask.report.is_(None),
                    ),
                ))
                rows = query.order_by(
                    TSkillEvalTask.updated_at.asc().nullsfirst(),
                    TSkillEvalTask.created_at.asc(),
                ).limit(limit).all()
                return [r.to_dict() for r in rows]
            except SQLAlchemyError as e:
                logger.error(f"查询待轮询Skill评测任务失败: {e}")
                raise

    def mark_stale_skill_eval_tasks_failed(self, timeout_seconds: int) -> int:
        """将超时任务标记为失败，同事务刷新相关批次；仍返回影响行数。"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=timeout_seconds)
        with self.connector.session_context() as session:
            try:
                # 先锁定并保留受影响任务和批次，不能等 failed 被轮询查询排除后
                # 再通过轮询结果收集批次。锁也避免超时更新覆盖并发完成的任务。
                rows = session.query(
                    TSkillEvalTask.id, TSkillEvalTask.batch_id,
                ).filter(
                    or_(
                        ~TSkillEvalTask.status.in_(["completed", "failed"]),
                        (TSkillEvalTask.status == "completed") & TSkillEvalTask.report.is_(None),
                    ),
                    TSkillEvalTask.created_at < cutoff,
                ).with_for_update().all()

                if not rows:
                    return 0

                task_ids = [row.id for row in rows]
                batch_ids = sorted({row.batch_id for row in rows})
                count = session.query(TSkillEvalTask).filter(
                    TSkillEvalTask.id.in_(task_ids),
                ).update({
                    TSkillEvalTask.status: "failed",
                    TSkillEvalTask.error: "评测超时",
                    TSkillEvalTask.updated_at: now,
                }, synchronize_session=False)

                # 使用当前 session，避免内部另开事务；任一批次汇总失败时，
                # 超时更新一起回滚，下一轮仍可重试这些任务。
                for batch_id in batch_ids:
                    self.refresh_skill_eval_batch_stats_in_session(session, batch_id)
                session.commit()
                return count
            except (SQLAlchemyError, ValueError) as error:
                session.rollback()
                logger.error(f"标记超时Skill评测任务并刷新批次失败: {error}")
                raise

    def refresh_skill_eval_batch_stats_in_session(self, session, batch_id: str) -> dict:
        """共用汇总逻辑；事务提交/回滚由调用者负责。"""
        batch = session.query(TSkillEvalBatch).filter(
            TSkillEvalBatch.id == batch_id,
        ).with_for_update().first()
        if not batch:
            raise ValueError(f"Skill评测批次 {batch_id} 不存在")

        rows = session.query(
            TSkillEvalTask.status, func.count(TSkillEvalTask.id),
        ).filter(
            TSkillEvalTask.batch_id == batch_id,
        ).group_by(TSkillEvalTask.status).all()
        counts = {status: count for status, count in rows}
        total = sum(counts.values())
        completed = counts.get("completed", 0)
        failed = counts.get("failed", 0)
        # 所有非终态都算未结束，避免未知/新增状态被误判为已完成。
        active = total - completed - failed
        if active > 0:
            batch_status = "processing"
        elif failed > 0:
            batch_status = "failed"
        elif total > 0:
            batch_status = "done"
        else:
            # 保持原实现对空批次的行为。
            batch_status = "failed"

        batch.total_count = total
        batch.completed_count = completed
        batch.failed_count = failed
        batch.status = batch_status
        batch.updated_at = datetime.now()
        session.flush()
        return {"total_count": total, "completed_count": completed,
                "failed_count": failed, "status": batch_status}

    def refresh_skill_eval_batch_stats(self, batch_id: str) -> dict:
        """按任务状态重算并保存批次统计与状态。"""
        with self.connector.session_context() as session:
            try:
                result = self.refresh_skill_eval_batch_stats_in_session(session, batch_id)
                session.commit()
                return result
            except (SQLAlchemyError, ValueError) as error:
                session.rollback()
                logger.error(f"刷新Skill评测批次统计失败: {error}")
                raise
