import openai
import xxhash

# from jinjamator.plugins.content import file
# from jinjamator.plugins.content import json

import os


def _get_missing_openai_connection_vars():
    inject = []
    if not _jinjamator.configuration._data["openai_access_token"]:
        inject.append("openai_access_token")
    return inject


def get_cache_dir():
    if not "openai_cache_dir" in _jinjamator.configuration._data:
        _jinjamator.configuration._data[
            "openai_cache_dir"
        ] = f"{_jinjamator._configuration['jinjamator_user_directory']}/cache/openai"
    file.mkdir_p(_jinjamator.configuration._data["openai_cache_dir"])
    return _jinjamator.configuration._data["openai_cache_dir"]


def get_cache_file_path(prompt):
    digest = xxhash.xxh64(prompt).hexdigest()
    cache_filename = get_cache_dir() + os.path.sep + digest + ".json"
    log.debug(f"using cache_filename {cache_filename}")
    return cache_filename


def get_cached_value(prompt):
    file_path = get_cache_file_path(prompt)
    if file.exists(file_path):
        return file_path, json.loads(file.load(file_path))
    else:
        return file_path, None


def cache_value(prompt, data):
    file_path = get_cache_file_path(prompt)
    digest = xxhash.xxh64(prompt).hexdigest()
    file.save(data, file_path)


def generate(
    prompt,
    disable_cache=False,
    model="text-davinci-003",
    temperature=0,
    max_tokens=3000,
    index=0,
    _requires=_get_missing_openai_connection_vars,
):
    if not _jinjamator.configuration["openai_access_token"]:
        _jinjamator.handle_undefined_var("openai_access_token")
    openai.api_key = _jinjamator.configuration["openai_access_token"]
    cache_filepath, cache_data = get_cached_value(prompt)
    if cache_data and not disable_cache:
        log.debug(f"using cache data from {cache_filepath}")
        return cache_data["choices"][index]
    else:
        log.debug(f"cache entry not found {cache_filepath}")
        response = str(
            openai.Completion.create(
                model=model,
                prompt=prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        )
        d = json.loads(response)
        d["prompt"] = prompt
        cache_value(prompt, json.dumps(d))
        return d["choices"][index]
