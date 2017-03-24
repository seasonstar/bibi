import json
from flask import Blueprint, jsonify, request, Response, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _
from configs.regions_list import REGION_HIERARCHY
import application.models as Models
from application.services.cache import cached


address = Blueprint('address', __name__, url_prefix='/api/address')


@address.route('/hierarchy', methods=['GET'])
@cached(21600)
def get_countries():
    return jsonify(message='OK', countries=list(REGION_HIERARCHY.keys()))


@address.route('/hierarchy/<country>', methods=['GET'])
@cached(21600)
def get_regions(country):
    regions = REGION_HIERARCHY.get(country)
    return jsonify(message='OK', regions=regions)


@address.route('/default', methods=['GET'])
@login_required
def default_address():
    addresses = current_user.addresses
    if len(addresses) > 0:
        return jsonify(message='OK', address=addresses[0].to_json())
    return jsonify(message='OK', address=None)


@address.route('/get/<addr_id>', methods=['GET'])
@login_required
def get_address(addr_id):
    address = Models.Address.objects(id=addr_id).first()
    if address not in current_user.addresses:
        return jsonify(message='Failed',
                       error=_('invalid address id for current user'))

    return jsonify(message='OK', address=address.to_json())

@address.route('/all', methods=['GET'])
@login_required
def user_addresses():
    addresses = current_user.addresses
    return jsonify(message='OK', addresses=[a.to_json() for a in addresses])


@address.route('/add', methods=['POST'])
@login_required
def address_add():
    contact = request.json
    address = Models.Address(
        state=contact['state'],
        city=contact['city'],
        country=contact['country'],
        street1=contact['street1'],
        street2=contact.get('street2'),
        postcode=contact['postcode'],
        receiver=contact['receiver'],
        mobile_number=contact['mobile_number']
        )
    address.save()

    current_user.addresses.insert(0, address)
    current_user.save()

    return jsonify(message='OK', address_id=str(address.id))


@address.route('/del/<addr_id>', methods=['GET'])
@login_required
def address_del(addr_id):
    address = Models.Address.objects(id=addr_id).first_or_404()
    if address not in current_user.addresses:
        return jsonify(message='Failed',
                       error=_('invalid address id for current user'))
    current_user.update(pull__addresses=address)
    address.delete()
    return jsonify(message='OK')


@address.route('/update/<addr_id>', methods=['POST'])
@login_required
def address_update(addr_id):
    address = Models.Address.objects(id=addr_id).first_or_404()
    if address not in current_user.addresses:
        return jsonify(message='Failed',
                       error=_('invalid address id for current user'))

    contact = request.json

    try:
        address.state=contact['state']
        address.city=contact['city']
        address.country=contact['country']
        address.street1=contact['street1']
        address.street2=contact.get('street2')
        address.postcode=contact['postcode']
        address.receiver=contact['receiver']
        address.mobile_number=contact['mobile_number']
    except KeyError:
        return jsonify(message='Failed',
                       error=_('invalid data'))
    address.save()

    return jsonify(message='OK', address_id=str(address.id))
