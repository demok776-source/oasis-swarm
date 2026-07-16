# Cloud Run does not support Kubernetes-style ConfigMap volumes (see
# https://docs.cloud.google.com/run/docs/migrate/from-kubernetes -- "Cloud Run
# does not have an equivalent of Kubernetes ConfigMaps"). ws-proxy-service.yaml
# previously tried to mount one anyway, which `gcloud run services replace`
# would reject outright. Baking the nginx config into the image is the
# standard fix for exactly this situation.
FROM nginx:alpine
COPY nginx-ws.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
