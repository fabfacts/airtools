from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

jobstores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
executors = {
    "default": ThreadPoolExecutor(5),
}
job_defaults = {"coalesce": False, "max_instances": 3}
