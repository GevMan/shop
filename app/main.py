from app import app
from app import db
import view
from links.profile import links
from links.blog import links_blog



app.register_blueprint(links,url_prefix='/')
app.register_blueprint(links_blog,url_prefix='/')



if __name__ == '__main__':
  
    app.run()
