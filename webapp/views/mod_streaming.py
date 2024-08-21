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


@mod_streaming_view.route('/mats')
@check_and_apply_event
@check_is_registered
def mats():
    if not g.device.event_role.may_use_beamer:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    if g.device.position.is_mat:
        assigned_mats = [g.device.position]
    else:
        assigned_mats = g.event.device_positions.filter_by(is_mat=True).all()

    stream = mats_stream(assigned_mats)
    stream = stream_with_context(stream)

    return Response(stream,
            mimetype='multipart/x-mixed-replace; boundary=frame')


def matches_stream(mats):
    match_base_frame = Image.open('./static/stream_frames/match_base_frame.png')

    while True:
        frame = Image.new('RGB', (match_base_frame.width, (match_base_frame.height) * len(mats) - 5))
        frame_draw = ImageDraw.Draw(frame)

        y = 0
        for m in mats:
            frame.paste(match_base_frame, (0, y))

            cm = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'exists'))

            if not cm:
                # Write mat number a bit lowered
                draw_text(frame_draw, 57.5, y+67.5, m.title.split(" ")[1], size=70, bold=True, color='white', alignment='center')

                y += match_base_frame.height
                continue


            # Write mat number
            draw_text(frame_draw, 57.5, y+40, m.title.split(" ")[1], size=70, bold=True, color='white', alignment='center')

            group_title = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'group_title'))
            white_name = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'white.name'))
            white_assoc = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'white.association'))
            blue_name = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'blue.name'))
            blue_assoc = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'blue.association'))
            

            draw_text(frame_draw, 57.5, y+110, group_title.replace(" ", "\n", 1), size=24, color='white', alignment='center')

            draw_text(frame_draw, 120, y+5, white_name, size=32, bold=True, color='black')
            draw_text(frame_draw, 120, y+45, white_assoc, size=18, color='black')

            draw_text(frame_draw, 120, y+80, blue_name, size=32, bold=True, color='white')
            draw_text(frame_draw, 120, y+120, blue_assoc, size=18, color='white')

            y += match_base_frame.height
        
        frame_byte_arr = io.BytesIO()
        frame.save(frame_byte_arr, format='PNG')

        yield (b'--frame\r\n'
                b'Content-Type: image/png\r\n\r\n' + frame_byte_arr.getvalue() + b'\r\n')
        
        time.sleep(1)



def mats_stream(mats):
    match_base_frame = Image.open('./static/stream_frames/mat_base_frame.png')

    while True:
        frame = Image.new('RGB', (match_base_frame.width, (match_base_frame.height) * len(mats) - 5))
        frame_draw = ImageDraw.Draw(frame)

        y = 0
        for m in mats:
            frame.paste(match_base_frame, (0, y))

            cm = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'exists'))

            # Write mat number
            draw_text(frame_draw, 57.5, y+45, m.title.split(" ")[1], size=70, bold=True, color='white', alignment='center')

            if not cm:
                y += match_base_frame.height
                continue

            group_title = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'group_title'))
            white_name = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'white.name'))
            white_assoc = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'white.association'))
            blue_name = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'blue.name'))
            blue_assoc = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'current_match', 'blue.association'))
            

            draw_text(frame_draw, 605, y+35, group_title.replace(" ", "\n", 1), size=20, color='white', alignment='center')

            draw_text(frame_draw, 120, y+5, white_name, size=32, bold=True, color='black')
            draw_text(frame_draw, 120, y+45, white_assoc, size=18, bold=True, color='black')

            draw_text(frame_draw, 650, y+5, blue_name, size=32, bold=True, color='white')
            draw_text(frame_draw, 650, y+45, blue_assoc, size=18, bold=True, color='white')

            wm = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'waiting_match', 'exists'))

            if not wm:
                y += match_base_frame.height
                continue

            group_title = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'waiting_match', 'group_title'))
            white_name = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'waiting_match', 'white.name'))
            white_assoc = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'waiting_match', 'white.association'))
            blue_name = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'waiting_match', 'blue.name'))
            blue_assoc = helpers.streaming.get_value(helpers.streaming.make_key(m.id, 'waiting_match', 'blue.association'))

            draw_text(frame_draw, 605, y+94, group_title.replace(" ", "\n", 1), size=12, color="#eee", alignment='center')
            draw_text(frame_draw, 120, y+83, f"{white_name} ({white_assoc})"[:40], size=20, color='#333')
            draw_text(frame_draw, 650, y+83, f"{blue_name} ({blue_assoc})"[:40], size=20, color='#eee')

            y += match_base_frame.height
        
        frame_byte_arr = io.BytesIO()
        frame.save(frame_byte_arr, format='PNG')

        yield (b'--frame\r\n'
                b'Content-Type: image/png\r\n\r\n' + frame_byte_arr.getvalue() + b'\r\n')
        
        time.sleep(1)



def draw_text(frame, x, y, text, *, font='arial', size=16, color='black', bold=False, alignment='left'):
    if bold:
        font = ImageFont.truetype(f'{font}bd.ttf', size)
    else:
        font = ImageFont.truetype(f'{font}.ttf', size)

    _, _, w, h = frame.textbbox((0, 0), text, font=font)

    if alignment == 'right':
        x -= w
        y -= h
    
    elif alignment == 'center':
        x -= w/2
        y -= h/2

    frame.text((x, y), text, font=font, align=alignment, fill=color)