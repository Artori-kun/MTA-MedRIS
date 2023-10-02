from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from RIS import app
from RIS.utils import util_cbir
from RIS.forms import CbirSearchForm
import secrets
import os
# import jsonify

## route for cbir api

## api parameters
## x0, x1, y0, y1: ROI coordinate
## instance_id: dicom instance ID
@app.route("/api/cbir/<sop_instance_uid>", methods=['GET'])
def api_cbir(sop_instance_uid):
    # sop_instance_uid = request.args.get('sop_uid')
    # print("It's here")
    try:
        x0 = request.form["x0"]
        y0 = request.form["y0"]
        x1 = request.form["x1"]
        y1 = request.form["y1"]
    except Exception as e:
        print(e)
        x0 = y0 = x1 = y1 = None
    
    cbir_result = util_cbir.cbir_search(sop_instance_id=sop_instance_uid,
                          x0=x0,
                          y0=y0,
                          x1=x1,
                          y1=y1)
    
    print(type(cbir_result))
    
    return jsonify(cbir_result)

@app.route("/cbir_search", methods = ['GET', 'POST'])
def cbir_search():
    org_instance_path = ''
    result_image_path = []
    search_clicked = False
    form = CbirSearchForm()

    session_uid = secrets.token_hex(10)
    session_path = os.path.join(app.root_path, 'static/temps/', session_uid)
    

    if request.method == 'POST' and form.validate_on_submit():
        os.mkdir(session_path)
        search_clicked = True
        x0 = y0 = x1 = y1 = None

        org_instance_id = form.search.data
        try:
            cbir_result = util_cbir.cbir_search(sop_instance_id=org_instance_id,
                            x0=x0,
                            y0=y0,
                            x1=x1,
                            y1=y1)
            
            # print(cbir_result)
            
            # save org image
            org_instance_path = os.path.join('temps', session_uid, org_instance_id + ".png")
            util_cbir.save_instance_image(os.path.join(app.root_path, 'static', org_instance_path), org_instance_id)

            # save result image
            counter = 0
            for id in cbir_result.keys():
                if counter > 10:
                    break
                img_path = os.path.join('temps', session_uid, id + ".png")
                print(img_path)
                result_image_path.append(img_path)

                util_cbir.save_instance_image(os.path.join(app.root_path, 'static', img_path), id)
                
                counter = counter + 1
        except Exception as e:
            print(e)
            flash('Couldnt resolve instance id', 'danger')
            return redirect(url_for("cbir_search"))
    # else:
    #     util_cbir.delete_files_and_subdirectories(os.path.join(app.root_path, 'static/temps/'))
    return render_template("cbir_search.html", 
                                   search_clicked=search_clicked, 
                                   org_instance_path = org_instance_path,
                                   result_image_path = result_image_path,
                                   form=form)

