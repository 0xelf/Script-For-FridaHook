 
import frida, sys
 
 
 
j2 = """
Java.perform(function() {
    console.log('进入')
    var URLClass = Java.use("java.net.URL");
    var HttpURLConnectionClass = Java.use("java.net.HttpURLConnection");
    URLClass.$init.overload('java.lang.String').implementation = function(url) {
        console.log("URL: " + url);
        return this.$init(url);
    };
    HttpURLConnectionClass.connect.implementation = function() {
        console.log("Connecting to: " + this.getURL().toString());
        // 获取堆栈信息
        var stackTrace = Java.use("android.util.Log").getStackTraceString(Java.use("java.lang.Exception").$new());
        console.log("Stack Trace: " + stackTrace);
        // 获取请求头信息
        console.log("Request Headers: " + JSON.stringify(this.getRequestProperties()));
        // 获取请求参数
        var requestMethod = this.getRequestMethod();
        if (requestMethod === 'POST') {
            var inputStream = this.getOutputStream();
            var byteArrayOutputStream = Java.use("java.io.ByteArrayOutputStream").$new();
            byteArrayOutputStream.writeTo.implementation = function(outputStream) {
                console.log("Request Data: " + this.toString());
                byteArrayOutputStream.writeTo(outputStream);
            };
            var bufferedWriter = Java.use("java.io.BufferedWriter").$new(Java.use("java.io.OutputStreamWriter").$new(inputStream));
            bufferedWriter.write.implementation = function(str) {
                console.log("Request Data: " + str);
                bufferedWriter.write(str);
            };
        }
        return this.connect();
    };
});
"""
 
def on_message(message, data):
    if message['type'] == 'send':
        print("[*]{0}".format(message['payload']))
    else:
        print(message)
 
process = frida.get_usb_device(-1).attach(10600)
# 可选择j1或者j2算法，使用起来功能一样，看哪个用的更顺手
script = process.create_script(j2)
script.on('message', on_message)
script.load()
# 不让程序断掉
sys.stdin.read()
