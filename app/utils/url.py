from app.models.config import config
def build_params_suffix(params:dict):
    params_suffix  = ";".join(map(lambda kv: f"{kv[0]}={kv[1]}",params.items()))
    # for key, value in params.items():
    #     params_suffix += f"{key}={value};"
    # return params_suffix[:-1]
    return params_suffix

def decode_param_to_dict(params:str):
    params = params.split(';')
    params_dict={}
    for param in params:
        param_k_v = param.split("=",1)
        params_dict[param_k_v[0]] = param_k_v[1]
    return params_dict


def build_url_with_preview(api,channel="",is_preview:bool=False):
    if is_preview:
        api += f";preview-id={config['api']['standard' if channel != 'imoney' else 'imoney']['preview-id']}"
    return api