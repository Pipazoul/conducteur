# conducteur



## Todo
- [ ] webhook
- [ ] check if container is stopped is running and start

## Quickstart

```bash
docker run --restart=unless-stopped  -p 8080:80 -v /var/run/docker.sock:/var/run/docker.sock 
-v ./id_rsa:/root/.ssh/id_rsa yassinsiouda/conducteur
```

## FAQ

### Set docker to remote access

```bash
https://docs.docker.com/config/daemon/remote-access/
```


## Ressources
https://codestrian.com/index.php/2023/03/29/expose-rootless-docker-api-socket-via-tcp-with-ssl/