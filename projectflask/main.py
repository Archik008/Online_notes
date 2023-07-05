from flask import Flask, render_template, url_for, request, redirect
import json
import datetime
import secrets

app = Flask(__name__)


user_data = {}

def save_data(get_data):
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(get_data, file, ensure_ascii=False, indent=4)

def load_data():
    global user_data
    with open('data.json', 'r', encoding='utf-8') as rfile:
       user_data = json.load(rfile)

def check_user(name, password):
    global user_data
    load_data()
    if name not in list(user_data.keys()) or password != user_data[name]['password']:
        return False
    return True

@app.route('/menu/<string:name>/<string:password>/<string:changed_note_id>', methods=['POST', 'GET'])
def menu(name, password, changed_note_id):
    if check_user(name, password):
        global user_data
        load_data()
        if request.method == 'POST':
            header = request.form['header']
            description = request.form['description']
            time = datetime.datetime.now().strftime("%H:%M")
            if changed_note_id == 'None':
                new_note_id = secrets.token_urlsafe(16)
                user_data[name][new_note_id] = {'description': description, 'time': time, 'header': header, 'id': new_note_id}
                save_data(user_data)
                names_notes = {}
                for key in user_data[name]:
                    if key != 'password':
                        names_notes[key] = user_data[name][key]
                return render_template('menu.html', notes=names_notes, username=name, has_notes=True, password=password)
            else:
                user_data[name][changed_note_id]['header'] = header
                user_data[name][changed_note_id]['description'] = description
                user_data[name][changed_note_id]['time'] = time
                save_data(user_data)
                names_notes = {}
                for key in user_data[name]:
                    if key != 'password':
                        names_notes[key] = user_data[name][key]
                return render_template('menu.html', notes=names_notes, username=name, has_notes=True, password=password)
        elif len(user_data[name].keys()) == 1:
            return render_template('menu.html', username=name, has_notes=False, password=password)
        else:
            names_notes = {}
            for key in user_data[name]:
                if key != 'password':
                    names_notes[key] = user_data[name][key]
            return render_template('menu.html', username=name, has_notes=True, notes=names_notes, password=password)

@app.route('/menu/<string:name>/<string:password>/add_note', methods=['POST', 'GET'])
def adding_note(name, password):
    if check_user(name, password):
        return render_template('add_note.html', username=name, password=password)
    return 'Доступ отказан'

@app.route('/menu/<string:name>/<string:password>/<string:note_id>/delete', methods=['POST'])
def delete_note(name, password, note_id):
    if check_user(name, password):
        global user_data
        load_data()
        del user_data[name][note_id]
        save_data(user_data)
        names_notes = {}
        for keyy in user_data[name]:
            if keyy != 'password':
                names_notes[keyy] = user_data[name][keyy]
        if len(user_data[name].keys()) == 1:
            return redirect(url_for('menu', name=name, password=password, changed_note_id='None'))
        else:
            return redirect(url_for('menu', name=name, password=password, changed_note_id='None'))
    return 'Доступ отказан'

@app.route('/menu/<string:name>/<string:password>/<string:note_id>/update', methods=['POST'])
def update_note(name, password, note_id):
    if check_user(name, password=password):
        global user_data
        load_data()
        header = user_data[name][note_id]['header']
        description = user_data[name][note_id]['description']
        save_data(user_data)
        return render_template('update_note.html', note_header=header, desc_note=description, note_id=note_id, username=name, password=password)


@app.route('/', methods=['POST', 'GET'])
def login_or_reg():
    if request.method == 'POST':
        global user_data
        load_data()
        newnick = request.form['newname']
        newpassword = request.form['password']
        with open('data.json', 'r', encoding='utf-8') as check_data:
            loaded_data = json.load(check_data)
            passwords = []
            if len(loaded_data) != 0:
                for dictionary in list(loaded_data.values()):
                    passwords.append(dictionary['password'])
                if newnick in list(loaded_data.keys()):
                    if loaded_data[newnick]['password'] == newpassword:
                        check_data.close()
                        return redirect(url_for('menu', name=newnick, password=newpassword, changed_note_id='None'))
                    else:
                        check_data.close()
                        return render_template('authorise.html', alert_text='Неправильный логин/пароль')
                elif newpassword in passwords:
                    check_data.close()
                    return render_template('authorise.html', alert_text='Придумайте другой пароль')
                else:
                    check_data.close()
                    user_data[newnick] = {'password': newpassword}
                    save_data(user_data)
                    return redirect(url_for('menu', name=newnick, password=newpassword, changed_note_id='None'))
            else:
                user_data[newnick] = {'password': newpassword}
                save_data(user_data)
                return redirect(url_for('menu', name=newnick, password=newpassword, changed_note_id='None'))
    else:
        return render_template('authorise.html')


if __name__ == '__main__':
    app.run(debug=True)