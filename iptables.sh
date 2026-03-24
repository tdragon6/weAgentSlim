#!/usr/bin/env zsh

source ~/.zshrc

# 创建无互联网网络
docker network create -d bridge -o com.docker.network.bridge.name=br-no-internet no-internet

# 清空DOCKER-USER ipables规则
sudo iptables -F DOCKER-USER
# 允许一切回流
sudo iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# 允许访问本地模型API，根据实际情况修改
sudo iptables -A DOCKER-USER -d 192.168.86.2 -p tcp --dport 1234 -j ACCEPT
# 拒绝no-internet网络的所有流量
sudo iptables -A DOCKER-USER -i br-no-internet -j DROP
# 拒绝访问其他一切内网
sudo iptables -A DOCKER-USER -d 10.0.0.0/8 -j DROP
sudo iptables -A DOCKER-USER -d 172.16.0.0/12 -j DROP
sudo iptables -A DOCKER-USER -d 192.168.0.0/16 -j DROP

# 查看当前DOCKER-USER ipables规则
sudo iptables -L DOCKER-USER -n -v --line-numbers