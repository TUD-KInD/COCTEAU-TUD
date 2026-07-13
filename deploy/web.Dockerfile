# Web (nginx) image: serves the static front-end and reverse-proxies the API.
# Build context is the repository root so the front-end can be copied in.
FROM nginx:1.25-alpine

# Replace the default site with our /periscope config.
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf

# Static front-end assets.
COPY front-end/ /usr/share/nginx/html/
