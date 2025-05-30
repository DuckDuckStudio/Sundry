import keyring

# GitHub 访问令牌
def read_token():
    # 凭据 github-access-token.glm
    try:
        token = keyring.get_password("github-access-token.glm", "github-access-token")
        if token is None:
            print(f"你可能还没设置glm的Token, 请尝试使用以下命令设置Token:\n    glm config --token <YOUR-TOKEN>\n")
            return 0
        # else:
        return token
    except Exception as e:
        print(f"✕ 读取Token时出错:\n{e}")
        return 0
