"""Data models used to organize data mostly for sending to the presentation layer.


"""

import helpers

class SiteStats(object):
  """Class that, when initialized, collects and organizes
  site-wide statistics about the data it is analyzing:
  number of papers indexed, number of authors profiled etc.

  """
  def __init__(self, connection):
    resp = connection.read("SELECT COUNT(id) FROM articles;")
    if len(resp) != 1 or len(resp[0]) != 1:
      self.paper_count = 0
    else:
      self.paper_count = resp[0][0]

    resp = connection.read("SELECT COUNT(id) FROM authors;")
    if len(resp) != 1 or len(resp[0]) != 1:
      self.author_count = 0
    else:
      self.author_count = resp[0][0]

class Author(object):
  """Class organizing the basic facts about a single
  author. Most other traits (rankings, a list of all
  publications, etc.) is appended later.
  """
  def __init__(self, id, first, last):
    self.id = id
    self.articles = []
    self.given = first
    self.surname = last
    if self.surname != "":
      self.full = "{} {}".format(self.given, self.surname)
    else:
      self.full = self.given
    self.downloads = 0
    self.rank = RankEntry()

class DateEntry(object):
  "Stores paper publication date info."
  def __init__(self, month, year):
    self.month = month
    self.year = year
    self.monthname = helpers.month_name(month)

class RankEntry(object):
  """Stores data about a paper's rank within a
  single corpus.
  """
  def __init__(self, rank=0, out_of=0, tie=False):
    self.rank = rank
    self.out_of = out_of
    self.tie = tie

class ArticleRanks(object):
  """Stores information about all of an individual article's
  rankings.
  """
  def __init__(self, alltime_count, alltime, ytd, lastmonth, collection):
    self.alltime = RankEntry(alltime, alltime_count)
    self.ytd = RankEntry(ytd, alltime_count)
    self.lastmonth = RankEntry(lastmonth, alltime_count)
    self.collection = RankEntry(collection)

class Article:
  """Base class for the different formats in which articles
  are presented throughout the site.
  """
  def __init(self):
    pass

  def get_authors(self, connection):
    """Fetches information about the paper's authors.

    Arguments:
      - connection: a database connection object.
    Returns nothing. Sets the article's "authors" field to
      a list of Author objects.

    """
    author_data = connection.read("SELECT authors.id, authors.given, authors.surname FROM article_authors as aa INNER JOIN authors ON authors.id=aa.author WHERE aa.article=%s;", (self.id,))
    self.authors = [Author(a[0], a[1], a[2]) for a in author_data]

  def GetDetailedTraffic(self, connection):
    data = connection.read("SELECT month, year, pdf FROM article_traffic WHERE article_traffic.article=%s ORDER BY year ASC, month ASC;", (self.id,))
    self.traffic = [TrafficEntry(entry) for entry in data]

class TrafficEntry(object):
  def __init__(self, sql_entry):
    self.month = sql_entry[0]
    self.year = sql_entry[1]
    self.downloads = sql_entry[2]

class SearchResultArticle(Article):
  "An article as displayed on the main results page."
  def __init__(self, sql_entry, connection):
    self.downloads = sql_entry[0]
    self.id = sql_entry[1]
    self.url = sql_entry[2]
    self.title = sql_entry[3]
    self.abstract = sql_entry[4]
    self.collection = sql_entry[5]
    self.date = DateEntry(sql_entry[6], sql_entry[7])
    self.get_authors(connection)

class TableSearchResultArticle(Article):
  "An article as displayed on the table-based main results page."
  def __init__(self, sql_entry, connection):
    self.alltime_downloads = sql_entry[0]
    self.ytd_downloads = sql_entry[1]
    self.month_downloads = sql_entry[2]
    self.id = sql_entry[3]
    self.url = sql_entry[4]
    self.title = sql_entry[5]
    self.abstract = sql_entry[6]
    self.collection = sql_entry[7]
    self.date = DateEntry(sql_entry[8], sql_entry[9])
    # NOTE: We won't get authors for these results until there's
    # a way to fetch the first author without sending a separate
    # query for each paper in the table.

class ArticleDetails(Article):
  "Detailed article info displayed on, i.e. author pages."
  def __init__(self, sql_entry, alltime_count, connection):
    self.downloads = sql_entry[0]
    self.ranks = ArticleRanks(alltime_count, sql_entry[1], sql_entry[2], sql_entry[3], sql_entry[9])
    self.id = sql_entry[4]
    self.url = sql_entry[5]
    self.title = sql_entry[6]
    self.abstract = sql_entry[7]
    self.collection = sql_entry[8]
    self.date = DateEntry(sql_entry[10], sql_entry[11])
    self.get_authors(connection)