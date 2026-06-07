static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          address: 0.0.0.0
          port_value: ${proxy_port}
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                codec_type: AUTO
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/"
                          route:
                            cluster: upstream_backend
                http_filters:
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  clusters:
    - name: upstream_backend
      type: STRICT_DNS
      connect_timeout: 5s
      load_assignment:
        cluster_name: upstream_backend
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: ${upstream_host}
                      port_value: ${upstream_port}

admin:
  address:
    socket_address:
      address: 0.0.0.0
      port_value: ${admin_port}

# FIX (28 Mayo 2026):
# Removed `bootstrap_extensions` section with `CompositeLogger`.
# Error: "could not find @type 'type.googleapis.com/envoy.extensions.log_config.bootstrap.composite_logger.v3.CompositeLogger'"
# Cause: This extension does NOT exist in envoyproxy/envoy:v1.30-latest.
#        It was likely copied from a newer/unreleased Envoy config example.
# Solution: Remove the entire `bootstrap_extensions` block. It's optional
#           and not needed for basic L7 proxy functionality.
# The `layered_runtime` section below is sufficient for resource limits.

layered_runtime:
  layers:
    - name: static_layer
      static_layer:
        envoy.resource_limits.listener.listener_0.connection_limit: 10000
