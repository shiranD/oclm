from flask import Flask, request, jsonify
import oclm
app = Flask(__name__)

print "READING LANGUAGE MODEL.."
path = TBD
lm = oclm.server(path)


@app.route('/state_update', methods=['POST'])
def lang_model():
    j = request.get_json()
    eegs = j['evidence']
    return_mode = j['return_mode']
    out = lm.state_update(eegs, return_mode)
    if return_mode == 'letter':
        return jsonify(letter=out)
    else:
        return jsonify(letter=out[0], word=out[1])


@app.route('/init', methods=['POST'])
def init():
    j = request.get_json()
    nbest = j['nbest']
    lm.init(nbest=nbest)
    return "succeded initing"


@app.route('/reset', methods=['POST'])
def reset():
    lm.reset()
    return "succeded reseting"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
