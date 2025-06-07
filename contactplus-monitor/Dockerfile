FROM nginx:alpine

# Copy the monitoring dashboard
COPY index.html /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 9090

# Start nginx
CMD ["nginx", "-g", "daemon off;"]