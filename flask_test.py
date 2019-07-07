from flask import Flask, request, abort
import bot_methods
import threading
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        dct = dict(request.form)
        print(dct)
        import broccoli_bot
        try:
            broccoli_bot.process_order(dct)
            return '', 200
        except Exception as e:
            bot_methods.send_message(broccoli_bot.admins_id[0], repr(e))
            return '', 200
    else:
        abort(400)


if __name__ != '__main__':
    threading.Thread(target=app.run, kwargs={'host':'0.0.0.0'}).start()

