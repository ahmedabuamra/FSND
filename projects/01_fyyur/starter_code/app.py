#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from flask_migrate import Migrate
import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# TODO: connect to a local postgresql database
db = SQLAlchemy(app)
migrate = Migrate(app, db) 

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Venue(db.Model):
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  address = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))

  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))

  def __repr__(self):
    return f'<Venue ID: {self.id}, name: {self.name}>'

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,          
      "city": self.city,         
      "state": self.state, 
      "address": self.address,            
      "phone": self.phone,      
      "genres": self.genres,                     
      "image_link": self.image_link,
      "facebook_link": self.facebook_link,     
      "website": self.website,        
      "seeking_venue": self.seeking_venue,
      "seeking_description": self.seeking_description
    }


class Artist(db.Model):
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)
  city = db.Column(db.String(120), nullable=False)
  state = db.Column(db.String(120), nullable=False)
  phone = db.Column(db.String(120))
  genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  # TODO: implement any missing fields, as a database migration using Flask-Migrate
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default=False)
  seeking_description = db.Column(db.String(500))
  venues = db.relationship('Venue', 
                            secondary='Show',
                            backref=db.backref("artists"))

  def __repr__(self):
    return f'<Artist ID: {self.id}, name: {self.name}>'

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,          
      "city": self.city,         
      "state": self.state,             
      "phone": self.phone,      
      "genres": self.genres,                     
      "image_link": self.image_link,
      "facebook_link": self.facebook_link,     
      "website": self.website,        
      "seeking_venue": self.seeking_venue,
      "seeking_description": self.seeking_description
    }


class Shows(db.Model):
  __tablename__ = 'Show'

  artist_id = db.Column(
    db.Integer, 
    db.ForeignKey('Artist.id'), 
    primary_key=True)
  venue_id = db.Column(
    db.Integer, 
    db.ForeignKey('Venue.id'), 
    primary_key=True)
  start_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
  artist = db.relationship(Artist, backref="shows")
  venue = db.relationship(Venue, backref="shows")

db.create_all()

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  STATE, CITY, NAME, ID = 0, 1, 2, 3
  venues = db.session.query(Venue.state, Venue.city, Venue.name, Venue.id).all()
  raw_data = {}
  for v in venues:
    if raw_data.get(v[STATE]) is None:
      raw_data[v[STATE]] = {}
    if raw_data[v[STATE]].get(v[CITY]) is None:
      raw_data[v[STATE]][v[CITY]] = []
    raw_data[v[STATE]][v[CITY]].append({
      "name": v[NAME],
      "id": v[ID],
    })
  data = []
  for state in raw_data:
    for city in raw_data[state]:
      data.append({
        "city": city,
        "state": state,
        "venues": raw_data[state][city]
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  name = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{name}%'))
  response={
    "count": venues.count(),
    "data": []
  }
  for venue in venues:
    response["data"].append({
      "id": venue.id,
      "name": venue.name
    })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  shows = Shows.query.filter_by(venue_id=venue_id)
  data = shows[0].venue.to_dict()
  data["upcoming_shows"] = []
  data["past_shows"] = []
  timenow = datetime.datetime.now()
  for show in shows:
    key = ""
    if show.start_time > timenow:
      key = "upcoming_shows"
    else:
      key = "past_shows"
    data[key].append({
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  data = dict((key, 
              request.form.getlist(key) if len(request.form.getlist(key)) > 1 
              else request.form.getlist(key)[0]) for key in request.form.keys())
  try:
    data['seeking_venue'] = True if data.get('seeking_venue') == 'y' else False
    venue = Venue(**data)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + data['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/    
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.', 'error')
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  NAME, ID = 0, 1
  artists = db.session.query(Artist.name, Artist.id).all()
  data = []
  for v in artists:
    data.append({
      "name": v[NAME],
      "id": v[ID],
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  name = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{name}%'))
  response={
    "count": artists.count(),
    "data": []
  }
  for artist in artists:
    response["data"].append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  shows = Shows.query.filter_by(artist_id=artist_id)
  data = shows[0].artist.to_dict()
  data["upcoming_shows"] = []
  data["past_shows"] = []
  timenow = datetime.datetime.now()
  for show in shows:
    key = ""
    if show.start_time > timenow:
      key = "upcoming_shows"
    else:
      key = "past_shows"
    data[key].append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    })
  data["past_shows_count"] = len(data["past_shows"])
  data["upcoming_shows_count"] = len(data["upcoming_shows"])
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  to_update = dict((key, 
              request.form.getlist(key) if len(request.form.getlist(key)) > 1 
              else request.form.getlist(key)[0]) for key in request.form.keys())
  artist = Artist.query.get(artist_id)
  try:
    artist.name = to_update.get("name")
    artist.city = to_update.get("city")
    artist.state = to_update.get("state")
    artist.address = to_update.get("address")
    artist.genres = to_update.get("genres")
    artist.phone = to_update.get("phone")
    artist.website = to_update.get("website")
    artist.facebook_link = to_update.get("facebook_link")
    artist.seeking_talent = to_update.get("seeking_talent")
    artist.seeking_description = to_update.get("seeking_description")
    artist.image_link = to_update.get("image_link")
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  to_update = dict((key, 
            request.form.getlist(key) if len(request.form.getlist(key)) > 1 
            else request.form.getlist(key)[0]) for key in request.form.keys())
  try:
    venue.name = to_update.get("name")
    venue.city = to_update.get("city")
    venue.state = to_update.get("state")
    venue.genres = to_update.get("genres")
    venue.phone = to_update.get("phone")
    venue.website = to_update.get("website")
    venue.facebook_link = to_update.get("facebook_link")
    venue.seeking_talent = to_update.get("seeking_talent")
    venue.seeking_description = to_update.get("seeking_description")
    venue.image_link = to_update.get("image_link")
    db.session.commit()
  except Exception as e:
    print(e)
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Artist record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  data = dict((key, 
              request.form.getlist(key) if len(request.form.getlist(key)) > 1 
              else request.form.getlist(key)[0]) for key in request.form.keys())
  try:
    data['seeking_venue'] = True if data.get('seeking_venue') == 'y' else False
    venue = Artist(**data)
    db.session.add(venue)
    db.session.commit()
    flash('Artist ' + data['name'] + ' was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/    
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.', 'error')
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  all_shows = Shows.query.all()
  data = []
  for show in all_shows:
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  data = dict((key, 
              request.form.getlist(key) if len(request.form.getlist(key)) > 1 
              else request.form.getlist(key)[0]) for key in request.form.keys())
  try:
    show = Shows(**data)
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except Exception as e:
    print(e)
    db.session.rollback()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/    
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
  app.run()
  
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
