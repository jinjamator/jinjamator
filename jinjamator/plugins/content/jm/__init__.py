import os

def get_job_log_files_dir():
    return os.path.join(_jinjamator._configuration.get("jinjamator_user_directory"),"logs", _jinjamator._configuration.get("jinjamator_job_id"),"files")
