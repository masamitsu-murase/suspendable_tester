# coding: utf-8

require("net/http")
require("openssl")
require("uri")
require("json")

def get(url, header=nil, limit=10)
    url = URI.parse(url)
    http = Net::HTTP.new(url.host, url.port)
    http.use_ssl = true
    # Just for test
    http.verify_mode = OpenSSL::SSL::VERIFY_NONE
    res = http.start do |h|
        req = Net::HTTP::Get.new(url.request_uri, header)
        h.request(req)
    end

    if res.kind_of?(Net::HTTPRedirection) && limit > 0
        get(res["location"], header, limit - 1)
    else
        res
    end
end

def main(python_exe_name, python_version)
    puts "Getting latest release information..."
    if python_version == "2"
        res = get("https://api.github.com/repos/masamitsu-murase/single_binary_stackless_python/releases/10437463")
    else
        res = get("https://api.github.com/repos/masamitsu-murase/single_binary_stackless_python/releases/latest")
    end
    latest_release_info = JSON.parse(res.body)

    puts "Finding #{python_exe_name}..."
    exe_url = latest_release_info["assets"].find{ |i| i["name"] == python_exe_name }["browser_download_url"]

    puts "Downloading #{python_exe_name}..."
    res = get(exe_url, { "Accept" => "application/octet-stream" })
    File.binwrite(python_exe_name, res.body.b)
end

main(ARGV[0], ARGV[1])
