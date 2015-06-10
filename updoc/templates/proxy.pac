/**
 * Provide the right proxy, given the URL and host.
 * @param url
 * @param host
 * @returns {string}
 */
function FindProxyForURL(url, host) {
    var ip = dnsResolve(host); // {% for proxy in proxies %} {% with network=proxy.network %}{% if network %}
    if (isInNet(ip, "{{ network.network_address }}", "{{ network.netmask }}")) {
        return "{{ proxy.proxy_str }}";
    } // {% else %}
    if (/{{ proxy.host }}/.test(url)) {
        return "{{ proxy.proxy_str }}";
    } // {% endif %}{% endwith %}{% endfor %}
    return "{{ defaults }}";
}