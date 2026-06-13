"""
notifications.py
~~~~~~~~~~~~~~~~
Central email notification helpers for RentSathi Nepal.

All public functions accept plain model objects and fire emails in a
background thread so the HTTP request is never blocked.

Usage:
    from app.utils.notifications import (
        notify_booking_confirmed,
        notify_booking_rejected,
        notify_property_verified,
        notify_property_rejected,
        notify_owner_verified,
    )
"""

import threading
from datetime import datetime


# ── Internal helpers ─────────────────────────────────────────────────────────

def _send_async(app, msg):
    """Send a Flask-Mail message in a daemon thread."""
    def _run():
        with app.app_context():
            try:
                from app import mail
                mail.send(msg)
            except Exception as exc:
                app.logger.error('[notifications] Failed to send email: %s', exc)

    if not app.config.get('MAIL_USERNAME'):
        # Mail not configured — log to console for dev convenience
        app.logger.warning(
            '[notifications][DEV] Email not sent (MAIL_USERNAME not set). Subject: %s | To: %s',
            msg.subject, msg.recipients,
        )
        return

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def _make_message(subject, recipients, html):
    from flask_mail import Message
    return Message(subject=subject, recipients=recipients, html=html)


def _now():
    return datetime.utcnow()


# ── Email builders ────────────────────────────────────────────────────────────

def _html_booking_confirmed(booking, tenant):
    listings_url = _external_url('main.listings')
    bookings_url = _external_url('user.my_bookings')
    prop = booking.property
    return f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
body{{margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111}}
.w{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07)}}
.hd{{background:linear-gradient(135deg,#16a34a,#15803d);padding:36px 40px;text-align:center}}
.logo{{display:inline-flex;align-items:center;gap:10px;text-decoration:none}}
.li{{width:42px;height:42px;background:rgba(255,255,255,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.4rem}}
.ln{{color:#fff;text-align:left}}.ln b{{font-size:1.15rem;font-weight:700;line-height:1.1;display:block}}.ln small{{font-size:.75rem;opacity:.8}}
.bd{{padding:36px 40px}}
.hi{{font-size:1.05rem;font-weight:600;margin-bottom:10px}}
.txt{{color:#6b7280;line-height:1.7;margin-bottom:20px}}
.box{{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:18px 20px;margin-bottom:24px}}
.row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #dcfce7;font-size:.9rem}}
.row:last-child{{border-bottom:none}}
.lbl{{color:#6b7280}}.val{{font-weight:600;color:#111}}
.btn{{display:block;text-align:center;background:#16a34a;color:#fff!important;text-decoration:none;padding:13px 32px;border-radius:10px;font-weight:700;font-size:.95rem;margin:24px 0 8px}}
.note{{font-size:.78rem;color:#9ca3af;text-align:center}}
hr{{border:none;border-top:1px solid #f3f4f6;margin:24px 0}}
.ft{{padding:0 40px 28px;text-align:center;font-size:.78rem;color:#9ca3af;line-height:1.6}}
.ft a{{color:#16a34a;text-decoration:none}}
</style></head><body>
<div class="w">
  <div class="hd">
    <div class="logo">
      <div class="li">🏠</div>
      <div class="ln"><b>RentSathi</b><small>Nepal</small></div>
    </div>
  </div>
  <div class="bd">
    <p class="hi">Hi {tenant.full_name.split()[0]}, your booking is confirmed! ✅</p>
    <p class="txt">Great news — the owner has confirmed your booking request. Here are the details:</p>
    <div class="box">
      <div class="row"><span class="lbl">Property</span><span class="val">{prop.title}</span></div>
      <div class="row"><span class="lbl">Location</span><span class="val">{prop.city}{', ' + prop.district if prop.district else ''}</span></div>
      <div class="row"><span class="lbl">Move-in Date</span><span class="val">{booking.move_in_date.strftime('%B %d, %Y')}</span></div>
      <div class="row"><span class="lbl">Monthly Rent</span><span class="val">Rs. {float(prop.price):,.0f}</span></div>
      <div class="row"><span class="lbl">Status</span><span class="val" style="color:#16a34a">Confirmed</span></div>
    </div>
    <p class="txt">The owner will be in touch to arrange the final details. You can also reach them via the Messages section.</p>
    <a href="{bookings_url}" class="btn">View My Bookings</a>
    <p class="note">If you have questions, reply to this email or use in-app chat.</p>
  </div>
  <hr>
  <div class="ft">&copy; {_now().year} RentSathi Nepal &nbsp;·&nbsp; <a href="{listings_url}">Browse Listings</a></div>
</div>
</body></html>
"""


def _html_booking_rejected(booking, tenant):
    listings_url = _external_url('main.listings')
    bookings_url = _external_url('user.my_bookings')
    prop = booking.property
    return f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
body{{margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111}}
.w{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07)}}
.hd{{background:linear-gradient(135deg,#e11d48,#9f1239);padding:36px 40px;text-align:center}}
.logo{{display:inline-flex;align-items:center;gap:10px;text-decoration:none}}
.li{{width:42px;height:42px;background:rgba(255,255,255,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.4rem}}
.ln{{color:#fff;text-align:left}}.ln b{{font-size:1.15rem;font-weight:700;line-height:1.1;display:block}}.ln small{{font-size:.75rem;opacity:.8}}
.bd{{padding:36px 40px}}
.hi{{font-size:1.05rem;font-weight:600;margin-bottom:10px}}
.txt{{color:#6b7280;line-height:1.7;margin-bottom:20px}}
.box{{background:#fff1f2;border:1px solid #fecdd3;border-radius:10px;padding:18px 20px;margin-bottom:24px}}
.row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #ffe4e6;font-size:.9rem}}
.row:last-child{{border-bottom:none}}
.lbl{{color:#6b7280}}.val{{font-weight:600;color:#111}}
.btn{{display:block;text-align:center;background:#e11d48;color:#fff!important;text-decoration:none;padding:13px 32px;border-radius:10px;font-weight:700;font-size:.95rem;margin:24px 0 8px}}
hr{{border:none;border-top:1px solid #f3f4f6;margin:24px 0}}
.ft{{padding:0 40px 28px;text-align:center;font-size:.78rem;color:#9ca3af;line-height:1.6}}
.ft a{{color:#e11d48;text-decoration:none}}
</style></head><body>
<div class="w">
  <div class="hd">
    <div class="logo">
      <div class="li">🏠</div>
      <div class="ln"><b>RentSathi</b><small>Nepal</small></div>
    </div>
  </div>
  <div class="bd">
    <p class="hi">Hi {tenant.full_name.split()[0]}, your booking was not accepted.</p>
    <p class="txt">Unfortunately, the owner has declined your booking request for the following property:</p>
    <div class="box">
      <div class="row"><span class="lbl">Property</span><span class="val">{prop.title}</span></div>
      <div class="row"><span class="lbl">Location</span><span class="val">{prop.city}{', ' + prop.district if prop.district else ''}</span></div>
      <div class="row"><span class="lbl">Requested Move-in</span><span class="val">{booking.move_in_date.strftime('%B %d, %Y')}</span></div>
      <div class="row"><span class="lbl">Status</span><span class="val" style="color:#e11d48">Declined</span></div>
    </div>
    <p class="txt">Don't give up — there are plenty of other great properties available. Browse our listings to find your next home.</p>
    <a href="{listings_url}" class="btn">Browse Other Properties</a>
  </div>
  <hr>
  <div class="ft">&copy; {_now().year} RentSathi Nepal &nbsp;·&nbsp; <a href="{listings_url}">Browse Listings</a></div>
</div>
</body></html>
"""


def _html_property_verified(prop, owner):
    listings_url = _external_url('main.property_detail', property_id=prop.id)
    dashboard_url = _external_url('owner.dashboard')
    return f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
body{{margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111}}
.w{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07)}}
.hd{{background:linear-gradient(135deg,#3b82f6,#1d4ed8);padding:36px 40px;text-align:center}}
.logo{{display:inline-flex;align-items:center;gap:10px;text-decoration:none}}
.li{{width:42px;height:42px;background:rgba(255,255,255,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.4rem}}
.ln{{color:#fff;text-align:left}}.ln b{{font-size:1.15rem;font-weight:700;line-height:1.1;display:block}}.ln small{{font-size:.75rem;opacity:.8}}
.bd{{padding:36px 40px}}
.hi{{font-size:1.05rem;font-weight:600;margin-bottom:10px}}
.txt{{color:#6b7280;line-height:1.7;margin-bottom:20px}}
.badge{{display:inline-flex;align-items:center;gap:6px;background:#eff6ff;border:1px solid #bfdbfe;color:#1e40af;border-radius:99px;padding:6px 16px;font-size:.85rem;font-weight:600;margin-bottom:20px}}
.box{{background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:18px 20px;margin-bottom:24px}}
.row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #dbeafe;font-size:.9rem}}
.row:last-child{{border-bottom:none}}
.lbl{{color:#6b7280}}.val{{font-weight:600;color:#111}}
.btn{{display:block;text-align:center;background:#3b82f6;color:#fff!important;text-decoration:none;padding:13px 32px;border-radius:10px;font-weight:700;font-size:.95rem;margin:24px 0 8px}}
hr{{border:none;border-top:1px solid #f3f4f6;margin:24px 0}}
.ft{{padding:0 40px 28px;text-align:center;font-size:.78rem;color:#9ca3af;line-height:1.6}}
.ft a{{color:#3b82f6;text-decoration:none}}
</style></head><body>
<div class="w">
  <div class="hd">
    <div class="logo">
      <div class="li">🏠</div>
      <div class="ln"><b>RentSathi</b><small>Nepal</small></div>
    </div>
  </div>
  <div class="bd">
    <div class="badge">✅ Property Verified</div>
    <p class="hi">Hi {owner.full_name.split()[0]}, your property is now live!</p>
    <p class="txt">Our admin team has verified your listing. It is now publicly visible to thousands of tenants on RentSathi Nepal.</p>
    <div class="box">
      <div class="row"><span class="lbl">Property</span><span class="val">{prop.title}</span></div>
      <div class="row"><span class="lbl">Type</span><span class="val">{prop.property_type.capitalize()}</span></div>
      <div class="row"><span class="lbl">Location</span><span class="val">{prop.city}{', ' + prop.district if prop.district else ''}</span></div>
      <div class="row"><span class="lbl">Monthly Rent</span><span class="val">Rs. {float(prop.price):,.0f}</span></div>
      <div class="row"><span class="lbl">Status</span><span class="val" style="color:#3b82f6">Verified &amp; Live</span></div>
    </div>
    <a href="{listings_url}" class="btn">View Your Listing</a>
  </div>
  <hr>
  <div class="ft">&copy; {_now().year} RentSathi Nepal &nbsp;·&nbsp; <a href="{dashboard_url}">Owner Dashboard</a></div>
</div>
</body></html>
"""


def _html_property_rejected(prop, owner):
    dashboard_url = _external_url('owner.dashboard')
    edit_url = _external_url('owner.edit_property', property_id=prop.id)
    return f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
body{{margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111}}
.w{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07)}}
.hd{{background:linear-gradient(135deg,#f97316,#c2410c);padding:36px 40px;text-align:center}}
.logo{{display:inline-flex;align-items:center;gap:10px;text-decoration:none}}
.li{{width:42px;height:42px;background:rgba(255,255,255,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.4rem}}
.ln{{color:#fff;text-align:left}}.ln b{{font-size:1.15rem;font-weight:700;line-height:1.1;display:block}}.ln small{{font-size:.75rem;opacity:.8}}
.bd{{padding:36px 40px}}
.hi{{font-size:1.05rem;font-weight:600;margin-bottom:10px}}
.txt{{color:#6b7280;line-height:1.7;margin-bottom:20px}}
.box{{background:#fff7ed;border:1px solid #fed7aa;border-radius:10px;padding:18px 20px;margin-bottom:24px}}
.row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #ffedd5;font-size:.9rem}}
.row:last-child{{border-bottom:none}}
.lbl{{color:#6b7280}}.val{{font-weight:600;color:#111}}
.btn{{display:block;text-align:center;background:#f97316;color:#fff!important;text-decoration:none;padding:13px 32px;border-radius:10px;font-weight:700;font-size:.95rem;margin:24px 0 8px}}
.tips{{background:#f9fafb;border-radius:8px;padding:14px 16px;margin-bottom:20px;font-size:.85rem;color:#4b5563;line-height:1.8}}
hr{{border:none;border-top:1px solid #f3f4f6;margin:24px 0}}
.ft{{padding:0 40px 28px;text-align:center;font-size:.78rem;color:#9ca3af;line-height:1.6}}
.ft a{{color:#f97316;text-decoration:none}}
</style></head><body>
<div class="w">
  <div class="hd">
    <div class="logo">
      <div class="li">🏠</div>
      <div class="ln"><b>RentSathi</b><small>Nepal</small></div>
    </div>
  </div>
  <div class="bd">
    <p class="hi">Hi {owner.full_name.split()[0]}, your listing needs attention.</p>
    <p class="txt">Our admin team reviewed your property listing and it was not approved in its current state.</p>
    <div class="box">
      <div class="row"><span class="lbl">Property</span><span class="val">{prop.title}</span></div>
      <div class="row"><span class="lbl">Location</span><span class="val">{prop.city}{', ' + prop.district if prop.district else ''}</span></div>
      <div class="row"><span class="lbl">Status</span><span class="val" style="color:#f97316">Needs Review</span></div>
    </div>
    <div class="tips">
      <strong>Common reasons for rejection:</strong><br>
      • Incomplete or inaccurate property details<br>
      • Missing or unclear photos<br>
      • Ownership documents need updating<br>
      • Property description too brief
    </div>
    <p class="txt">Please update your listing and it will be re-submitted for review automatically.</p>
    <a href="{edit_url}" class="btn">Edit &amp; Resubmit</a>
  </div>
  <hr>
  <div class="ft">&copy; {_now().year} RentSathi Nepal &nbsp;·&nbsp; <a href="{dashboard_url}">Owner Dashboard</a></div>
</div>
</body></html>
"""


def _html_owner_verified(owner):
    dashboard_url = _external_url('owner.dashboard')
    add_url = _external_url('owner.add_property')
    return f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
body{{margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111}}
.w{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07)}}
.hd{{background:linear-gradient(135deg,#8b5cf6,#6d28d9);padding:36px 40px;text-align:center}}
.logo{{display:inline-flex;align-items:center;gap:10px;text-decoration:none}}
.li{{width:42px;height:42px;background:rgba(255,255,255,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.4rem}}
.ln{{color:#fff;text-align:left}}.ln b{{font-size:1.15rem;font-weight:700;line-height:1.1;display:block}}.ln small{{font-size:.75rem;opacity:.8}}
.bd{{padding:36px 40px}}
.hi{{font-size:1.1rem;font-weight:700;margin-bottom:10px}}
.txt{{color:#6b7280;line-height:1.7;margin-bottom:20px}}
.badge{{display:inline-flex;align-items:center;gap:6px;background:#f5f3ff;border:1px solid #ddd6fe;color:#5b21b6;border-radius:99px;padding:6px 16px;font-size:.85rem;font-weight:600;margin-bottom:20px}}
.perks{{background:#f5f3ff;border:1px solid #ddd6fe;border-radius:10px;padding:18px 20px;margin-bottom:24px;font-size:.88rem;color:#4b5563;line-height:2}}
.btn{{display:block;text-align:center;background:#8b5cf6;color:#fff!important;text-decoration:none;padding:13px 32px;border-radius:10px;font-weight:700;font-size:.95rem;margin:8px 0}}
.btn2{{display:block;text-align:center;background:#fff;border:1.5px solid #8b5cf6;color:#8b5cf6!important;text-decoration:none;padding:12px 32px;border-radius:10px;font-weight:600;font-size:.95rem;margin:8px 0}}
hr{{border:none;border-top:1px solid #f3f4f6;margin:24px 0}}
.ft{{padding:0 40px 28px;text-align:center;font-size:.78rem;color:#9ca3af;line-height:1.6}}
.ft a{{color:#8b5cf6;text-decoration:none}}
</style></head><body>
<div class="w">
  <div class="hd">
    <div class="logo">
      <div class="li">🏠</div>
      <div class="ln"><b>RentSathi</b><small>Nepal</small></div>
    </div>
  </div>
  <div class="bd">
    <div class="badge">🛡️ Verified Owner</div>
    <p class="hi">Congratulations, {owner.full_name.split()[0]}! You're now a Verified Owner.</p>
    <p class="txt">Your identity and documents have been reviewed and approved by our admin team. Your account now carries the Verified Owner badge.</p>
    <div class="perks">
      <strong>What this means for you:</strong><br>
      ✅ Verified badge on all your listings<br>
      ✅ Higher visibility in search results<br>
      ✅ Increased trust from tenants<br>
      ✅ Priority support from our team
    </div>
    <p class="txt">You can now list properties and start receiving booking requests.</p>
    <a href="{add_url}" class="btn">List a Property</a>
    <a href="{dashboard_url}" class="btn2">Go to Dashboard</a>
  </div>
  <hr>
  <div class="ft">&copy; {_now().year} RentSathi Nepal &nbsp;·&nbsp; <a href="{dashboard_url}">Owner Dashboard</a></div>
</div>
</body></html>
"""


def _html_owner_rejected(owner):
    profile_url = _external_url('owner.owner_profile')
    return f"""
<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<style>
body{{margin:0;padding:0;background:#f3f4f6;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#111}}
.w{{max-width:560px;margin:40px auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07)}}
.hd{{background:linear-gradient(135deg,#6b7280,#374151);padding:36px 40px;text-align:center}}
.logo{{display:inline-flex;align-items:center;gap:10px;text-decoration:none}}
.li{{width:42px;height:42px;background:rgba(255,255,255,.2);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.4rem}}
.ln{{color:#fff;text-align:left}}.ln b{{font-size:1.15rem;font-weight:700;line-height:1.1;display:block}}.ln small{{font-size:.75rem;opacity:.8}}
.bd{{padding:36px 40px}}
.hi{{font-size:1.05rem;font-weight:600;margin-bottom:10px}}
.txt{{color:#6b7280;line-height:1.7;margin-bottom:20px}}
.tips{{background:#f9fafb;border-radius:8px;padding:14px 16px;margin-bottom:20px;font-size:.85rem;color:#4b5563;line-height:1.8}}
.btn{{display:block;text-align:center;background:#374151;color:#fff!important;text-decoration:none;padding:13px 32px;border-radius:10px;font-weight:700;font-size:.95rem;margin:24px 0 8px}}
hr{{border:none;border-top:1px solid #f3f4f6;margin:24px 0}}
.ft{{padding:0 40px 28px;text-align:center;font-size:.78rem;color:#9ca3af;line-height:1.6}}
</style></head><body>
<div class="w">
  <div class="hd">
    <div class="logo">
      <div class="li">🏠</div>
      <div class="ln"><b>RentSathi</b><small>Nepal</small></div>
    </div>
  </div>
  <div class="bd">
    <p class="hi">Hi {owner.full_name.split()[0]}, your verification needs more information.</p>
    <p class="txt">Our admin team reviewed your owner verification documents and could not approve them at this time.</p>
    <div class="tips">
      <strong>Please check the following:</strong><br>
      • Citizenship front and back images are clear and readable<br>
      • Citizenship number is correctly entered<br>
      • Owner type (individual / agency) is selected<br>
      • All required fields in your profile are filled
    </div>
    <p class="txt">Please update your profile with correct documents and our team will review again shortly.</p>
    <a href="{profile_url}" class="btn">Update My Profile</a>
  </div>
  <hr>
  <div class="ft">&copy; {_now().year} RentSathi Nepal</div>
</div>
</body></html>
"""


# ── URL helper (works outside request context) ────────────────────────────────

def _external_url(endpoint, **values):
    from flask import url_for
    try:
        return url_for(endpoint, _external=True, **values)
    except Exception:
        return '#'


# ── Public API ────────────────────────────────────────────────────────────────

def notify_booking_confirmed(booking):
    """Send booking confirmation email to the tenant."""
    from flask import current_app
    app = current_app._get_current_object()
    tenant = booking.tenant
    msg = _make_message(
        subject=f'✅ Booking Confirmed — {booking.property.title}',
        recipients=[tenant.email],
        html=_html_booking_confirmed(booking, tenant),
    )
    _send_async(app, msg)


def notify_booking_rejected(booking):
    """Send booking rejection email to the tenant."""
    from flask import current_app
    app = current_app._get_current_object()
    tenant = booking.tenant
    msg = _make_message(
        subject=f'Booking Update — {booking.property.title}',
        recipients=[tenant.email],
        html=_html_booking_rejected(booking, tenant),
    )
    _send_async(app, msg)


def notify_property_verified(prop):
    """Send property verified email to the property owner."""
    from flask import current_app
    app = current_app._get_current_object()
    owner = prop.owner
    msg = _make_message(
        subject=f'✅ Your listing "{prop.title}" is now live!',
        recipients=[owner.email],
        html=_html_property_verified(prop, owner),
    )
    _send_async(app, msg)


def notify_property_rejected(prop):
    """Send property rejected email to the property owner."""
    from flask import current_app
    app = current_app._get_current_object()
    owner = prop.owner
    msg = _make_message(
        subject=f'Action Required — "{prop.title}" needs updates',
        recipients=[owner.email],
        html=_html_property_rejected(prop, owner),
    )
    _send_async(app, msg)


def notify_owner_verified(owner_profile):
    """Send owner verified email to the owner."""
    from flask import current_app
    app = current_app._get_current_object()
    owner = owner_profile.user
    msg = _make_message(
        subject='🛡️ You are now a Verified Owner on RentSathi Nepal',
        recipients=[owner.email],
        html=_html_owner_verified(owner),
    )
    _send_async(app, msg)


def notify_owner_rejected(owner_profile):
    """Send owner verification rejected email."""
    from flask import current_app
    app = current_app._get_current_object()
    owner = owner_profile.user
    msg = _make_message(
        subject='Owner Verification — Additional Information Required',
        recipients=[owner.email],
        html=_html_owner_rejected(owner),
    )
    _send_async(app, msg)
