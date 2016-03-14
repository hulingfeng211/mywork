### 角色管理
#### 页面
* `/page/role`        角色管理  对应的模板`role.mgt.html`
* `/page/role/choice`  角色列表选择  **[未开发]**

### 服务
* `/s/role`  角色保存(`post`)和查询(`get`)
* `/s/role/menus?role_id=xxxx` 获取角色下的菜单(`get`)/保存角色菜单（`post`)
* `/s/role/perms?role_id=xxxx` 获取角色下的权限(`get`)/保存角色权限（`post`)
* `/s/login/roles` 获取所有的角色(`get`),绕过xsrf检查

---

### 用户管理
#### 页面
* `/page/user` 用户管理 对应的模板 `user.mgt.html`
* `/page/role/user` 角色用户管理 对应的模板`role.user.html`
#### 服务
* `/s/user` 用户查询(`get`)和保存(`post`)
* `/s/user/roles?user_id=xxxx` 查询(`get`)和保存(`post`)用户角色  
* `/s/role/users?role_id=xxxx` 查询(`get`)和保存(`post`)用户的角色

---

### 权限管理
#### 页面
#### 服务

---

### 菜单管理
#### 页面
#### 服务

---

### 组织管理
#### 页面
#### 服务

---

### 人员管理
#### 页面
#### 服务

---
## 权限总表
| URL        | 功能描述           |     需要   |  角色     |      权限    |
| ------------- |-------------:| :-----:|:---------------:|:----:|  
| /app/      | 首页 |Y |所有 |所有   |
| /page/login      | 用户登录|N      |  所有 | 所有  |
| /s/onlineuser | 在线用户|Y      |    {"post":"root"} |{"post":"onelineuser:logout"}   |
| /s/perms | 权限管理服务|Y      |    {"post":"root"} |    |
| /s/orgns | 组织管理服务|Y      |    {"post":"root"} |    |
| /s/users | 用户管理服务|Y      |    {"post":"root"} |    |
| /s/users/(.+) | 查询用户信息服务|Y      |    {"post":"root"} |    |
| /s/roles | 角色管理服务|Y      |    {"post":"root"} |   |
| /s/menus | 菜单管理服务|Y      |    {"post":"root"} |    |

