# -*- coding: utf-8 -*-
import datetime
import json
from werkzeug.utils import secure_filename
from mongoengine.errors import ValidationError
from flask import request, jsonify, redirect, url_for, flash
from flask_admin import expose
from flask_babel import gettext as _
from application.extensions import admin
from application.controllers.admin import AdminView
import application.services.jobs as Jobs
import application.models as Models
from application.utils import redirect_url


class BannerView(AdminView):
    _permission = 'content'

    @expose('/', methods=['GET'])
    def index(self):
        banners = Models.Banner.objects().order_by('-order')
        return self.render('admin/content/banner.html',
                           banners=banners)

    @expose('/set/<id>', methods=['POST'])
    def set(self, id):
        banner = Models.Banner.objects(id=id).first()
        date_from = request.form.get('from')
        date_until = request.form.get('until')
        if date_from:
            try:
                dt = datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M')
            except ValueError:
                flash(_('Invalid date format. Example: 2014-07-30 20:00'), 'error')
            else:
                banner.date_from = dt
        if date_until:
            try:
                dt = datetime.datetime.strptime(date_until, '%Y-%m-%d %H:%M')
            except ValueError:
                flash(_('Invalid date format. Example: 2014-07-30 20:00'), 'error')
            else:
                banner.date_until = dt
        banner.target = request.form.get('target').strip()
        banner.banner_type = request.form.get('banner_type').strip()
        banner.save()
        flash('successfully updated')
        return redirect(redirect_url())

    @expose('/move', methods=['PATCH'])
    def move(self):
        a_from = request.form.get('from')
        a_to = request.form.get('to')
        if a_from and a_to:
            b_from = Models.Banner.objects(id=a_from).first_or_404()
            b_to = Models.Banner.objects(id=a_to).first_or_404()
            b_from.order, b_to.order = b_to.order, b_from.order
            b_from.save()
            b_to.save()
            return jsonify(message='OK', bfrom=b_from.order, bto=b_to.order)
        return jsonify(message="Failed")

    @expose('/unpublish/<id>', methods=['GET'])
    def unpublish(self, id):
        banner = Models.Banner.objects(id=id).first()
        banner.published = False
        banner.save()
        return redirect(redirect_url())

    @expose('/delete/<id>', methods=['GET'])
    def delete(self, id):
        banner = Models.Banner.objects(id=id).first()
        if banner:
            banner.delete()
        return redirect(redirect_url())

    @expose('/upload_img/<id>', methods=['POST'])
    def upload_img(self, id):
        banner = Models.Banner.objects(id=id).first()
        img = request.files.get('img')
        if img:
            name, ext = img.filename.rsplit('.', 1)
            name = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
            filename = secure_filename(name)
            path = '{}/{}.{}'.format('banner', filename, ext)
            url = Jobs.image.upload('maybi-img', path, image=img.read(), make_thumbnails=True)
            banner.img = url
            banner.save()

        return redirect(redirect_url())

    @expose('/upload', methods=['GET', 'POST'])
    def upload(self):
        if request.method == 'GET':
            return self.render('admin/content/upload.html')

        target = request.form.get('boardid', '')
        banner_type = request.form.get('banner_type')
        img = request.files.get('image')
        name, ext = img.filename.rsplit('.', 1)
        name = datetime.datetime.now().strftime('%Y-%m-%d-%H%M%S')
        filename = secure_filename(name)
        path = '{}/{}.{}'.format('banner', filename, ext)
        url = Jobs.image.upload('maybi-img', path, image=img.read(), make_thumbnails=True)


        # check if it is URL
        if banner_type == 'URL':
            if target.startswith('http') == False:
                flash(_('Upload failed. If you select Board, please fill in Board ID, otherwise fill in URL.'))
                return redirect(redirect_url())

        # then check if it valid ObjectID
        elif banner_type == 'BOARD':
            try:
                board = Models.Board.objects(id=target).first()
            except ValidationError:
                flash('Upload failed. please fill in a valid Board ID')
                return redirect(redirect_url())

        Models.Banner(banner_type=banner_type,
                target=target, img=url, published=True).save()
        flash(_('Upload successfully'))
        return redirect(url_for('bannerview.index'))


admin.add_view(BannerView(name='Banner', category='Content', menu_icon_type='fa', menu_icon_value='gift'))
