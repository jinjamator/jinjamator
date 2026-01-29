import os

def get_job_log_files_dir():
    path=os.path.join(_jinjamator._configuration.get("jinjamator_user_directory"),"logs", _jinjamator._configuration.get("jinjamator_job_id",str(id(_jinjamator))),"files")
    os.makedirs(path,exist_ok=True)
    return path 
    
def run_output_plugin(data):
    _jinjamator._output_plugin.connect()
    try:
        result=_jinjamator._output_plugin.process(data, template_path=_jinjamator._current_tasklet, current_data=_jinjamator.configuration)                
    except Exception as e:                
        error_text=_jinjamator.parse_exception(e,tasklet)
        self._log.error("Output Plugin failed: " + error_text)
        return False
    return True
