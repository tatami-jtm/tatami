from flask import Blueprint, flash, g, session, request, redirect, url_for, Response, stream_with_context

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db
from .. import helpers

import time, io

from PIL import Image, ImageDraw, ImageFont

mod_streaming_view = Blueprint('mod_streaming', __name__)

@mod_streaming_view.route('/matches')
@check_and_apply_event
@check_is_registered
def matches():
    if not g.device.event_role.may_use_beamer:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    if g.device.position.is_mat:
        assigned_mats = [g.device.position]
    else:
        assigned_mats = g.event.device_positions.filter_by(is_mat=True).all()

    stream = matches_stream(assigned_mats)
    stream = stream_with_context(stream)

    return Response(stream,
            mimetype='multipart/x-mixed-replace; boundary=frame')


def matches_stream(mats):
    match_base_frame = Image.open('./static/stream_frames/match_base_frame.png')

    while True:
        frame = Image.new('RGB', (match_base_frame.width, (match_base_frame.height) * len(mats)))
        frame_draw = ImageDraw.Draw(frame)

        y = 0
        for m in mats:
            frame.paste(match_base_frame, (0, y))

            # Write match number
            font = ImageFont.truetype('arialbd.ttf', 80)
            frame_draw.text((32, y+10), m.title.split(" ")[1], font=font)

            cm = m.current_match()
            if not cm: continue
            
            font = ImageFont.truetype('arial.ttf', 16)
            frame_draw.text((20, y+100), cm.group.title.replace(" ", "\n", 1), align="center", font=font)

            font = ImageFont.truetype('arialbd.ttf', 32)
            frame_draw.text((120, y+5), cm.white.full_name, font=font, fill='black')

            font = ImageFont.truetype('arial.ttf', 18)
            frame_draw.text((120, y+45), cm.white.association_name, font=font, fill='black')

            font = ImageFont.truetype('arialbd.ttf', 32)
            frame_draw.text((120, y+80), cm.blue.full_name, font=font, fill='white')

            font = ImageFont.truetype('arial.ttf', 18)
            frame_draw.text((120, y+120), cm.blue.association_name, font=font, fill='white')

            y += match_base_frame.height
        
        frame_byte_arr = io.BytesIO()
        frame.save(frame_byte_arr, format='PNG')

        yield (b'--frame\r\n'
                b'Content-Type: image/png\r\n\r\n' + frame_byte_arr.getvalue() + b'\r\n')
        
        time.sleep(1)