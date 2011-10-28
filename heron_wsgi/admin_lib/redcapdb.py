'''redcapdb -- a little ORM support for REDCap's EAV structure

'''

import injector
from injector import inject, provides, singleton
import sqlalchemy
from sqlalchemy import Table, Column, text
from sqlalchemy.types import INTEGER, VARCHAR, TEXT, Integer, String, DATETIME
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, column_property
from sqlalchemy.sql import join, and_, select

import config
from orm_base import Base

CONFIG_SECTION='redcapdb'

redcap_data = Table('redcap_data', Base.metadata,
                    Column(u'project_id', INTEGER(),
                           nullable=False, default=text(u"'0'"),
                           primary_key=True),
                    Column(u'event_id', INTEGER(), primary_key=True),
                    Column(u'record', VARCHAR(length=100), primary_key=True),
                    Column(u'field_name', VARCHAR(length=100),
                           primary_key=True),
                    Column(u'value', TEXT()),
                    )

# this is mostly for testing
redcap_surveys_response =  Table('redcap_surveys_response', Base.metadata,
    Column(u'response_id', INTEGER(), primary_key=True, nullable=False),
            Column(u'participant_id', INTEGER()),
            Column(u'record', VARCHAR(length=100)),
            Column(u'first_submit_time', DATETIME()),
            Column(u'completion_time', DATETIME()),
            Column(u'return_code', VARCHAR(length=8)),
    )
redcap_surveys_participants =  Table('redcap_surveys_participants', Base.metadata,
    Column(u'participant_id', INTEGER(), primary_key=True, nullable=False),
            Column(u'survey_id', INTEGER()),
            Column(u'arm_id', INTEGER()),
            Column(u'hash', VARCHAR(length=6)),
            Column(u'legacy_hash', VARCHAR(length=32)),
            Column(u'participant_email', VARCHAR(length=255)),
            Column(u'participant_identifier', VARCHAR(length=255)),
    )


def eachcol(t1, t2, cols):
    '''
      >>> pairs = eachcol(redcap_data, redcap_data,
      ...                 ['project_id', 'record'])
      >>> pairs[0][0].name
      u'project_id'
    '''
    # .columns is an OrderedDict, so we can correlate indexes.
    n1 = t1.columns.keys()
    n2 = t2.columns.keys()
    return [(t1.columns[n1[n2.index(col)]], t2.columns[col])
            for col in cols]


def colsmatch(t1, t2, cols):
    '''
      >>> exp = colsmatch(redcap_data, redcap_data.alias('x2'),
      ...                 ['project_id', 'record'])
      >>> print exp
      redcap_data.project_id = x2.project_id AND redcap_data.record = x2.record

    '''
    return and_(*[(t1c == t2c) for t1c, t2c in eachcol(t1, t2, cols)])


def eav_join(t, keycols, attrs, acol, vcol):
    '''
      >>> cols1, j1, w1 = eav_join(redcap_data,
      ...                          ['project_id', 'record'],
      ...                          ['url'],
      ...                          'field_name', 'value')
      >>> cols1
      [Column(u'value', TEXT(), table=<j_url>)]

      >>> print select(cols1).where(w1)
      SELECT j_url.value 
      FROM redcap_data AS j_url 
      WHERE j_url.field_name = :field_name_1

      >>> c2, j2, w2 = eav_join(redcap_data,
      ...                       ['project_id', 'record'],
      ...                       ['url', 'name'],
      ...                       'field_name', 'value')
      >>> print select(c2).where(w2)
      SELECT j_url.value, j_name.value 
      FROM redcap_data AS j_url, redcap_data AS j_name 
      WHERE j_url.field_name = :field_name_1 AND j_url.project_id = j_name.project_id AND j_url.record = j_name.record AND j_name.field_name = :field_name_2


      >>> c3, j3, w3 = eav_join(redcap_data,
      ...                       ['project_id', 'record'],
      ...                       ['disclaimer_id', 'url', 'current'],
      ...                       'field_name', 'value')
      >>> print select(c3).where(w3).apply_labels()
      SELECT j_disclaimer_id.value AS j_disclaimer_id_value, j_url.value AS j_url_value, j_current.value AS j_current_value 
      FROM redcap_data AS j_disclaimer_id, redcap_data AS j_url, redcap_data AS j_current 
      WHERE j_disclaimer_id.field_name = :field_name_1 AND j_disclaimer_id.project_id = j_url.project_id AND j_disclaimer_id.record = j_url.record AND j_url.field_name = :field_name_2 AND j_disclaimer_id.project_id = j_current.project_id AND j_disclaimer_id.record = j_current.record AND j_current.field_name = :field_name_3
      '''

    #aliases = dict([(n, t.alias('t_' + n)) for n in attrs])

    # use itertools rather than for loop for fold?
    #a0 = aliases[attrs[0]]
    t0 = t.alias('j_' + attrs[0])
    product = t0
    where = t0.columns[acol] == attrs[0]
    vcols = [t0.columns[vcol]]

    for n in attrs[1:]:
        tn = t.alias('j_' + n)
        wn = colsmatch(product, tn, keycols)
        where = and_(where, wn, (tn.columns[acol] == n))
        product = product.join(tn, wn)
        vcols.append(tn.columns[vcol])

    return vcols, product, where


class REDCapRecord(object):
    '''Abstract class that provides mapping of fields to redcap EAV structure.

    For testing, we'll use the example from import_records.php from REDCap API examples::
      >>> _TestRecord.fields
      ('study_id', 'age', 'sex')

    '''

    fields = ()

    def __repr__(self):
        '''
          >>> r = _TestRecord('test_001', 31, 0)
          >>> r
          _TestRecord(study_id=test_001, age=31, sex=0)
        '''
        return self.__class__.__name__ + '(' + (
            ', '.join(['%s=%s' % (f, getattr(self, f)) for f in self.fields])) + ')'

    @classmethod
    def eav_map(cls, project_id, alias='eav'):
        '''Set up the ORM mapping based on project_id.

        @param cls: class to map
        @param pid: redcap project id to select
        @param fields: 1st is primary key
        @return: (value_columns, join_where_clause)

          >>> cols, where = _TestRecord.eav_map(project_id=123)
          >>> [c.table.name for c in cols]
          ['j_study_id', 'j_age', 'j_sex']
          >>> str(where)
          'j_study_id.field_name = :field_name_1 AND j_study_id.project_id = j_age.project_id AND j_study_id.record = j_age.record AND j_age.field_name = :field_name_2 AND j_study_id.project_id = j_sex.project_id AND j_study_id.record = j_sex.record AND j_sex.field_name = :field_name_3'

          >>> smaker = Mock.make('')
          >>> s = smaker()
          >>> for project_id, record, field_name, value in (
          ...     (123, 1, 'study_id', 'test_002'),
          ...     (123, 1, 'age', 32),
          ...     (123, 1, 'sex', 1)):
          ...     s.execute(redcap_data.insert().values(event_id=321,
          ...                                           project_id=project_id, record=record,
          ...                                           field_name=field_name, value=value)) and None
          >>> s.commit()
          >>> s.query(_TestRecord).all()      
          [_TestRecord(study_id=test_002, age=32, sex=1)]

        '''
        data = redcap_data.select().where(redcap_data.c.project_id==project_id)
        cols, j, w = eav_join(data.alias(alias),
                              keycols=('project_id', 'record'),
                              attrs=cls.fields,
                              acol='field_name', vcol='value')

        mapper(cls, select(cols).where(w).apply_labels().alias(),
               primary_key=[cols[0]],
               properties=dict(zip(cls.fields, cols)))

        return cols, w


class _TestRecord(REDCapRecord):
    fields = ('study_id', 'age', 'sex')
    def __init__(self, study_id, age, sex):
        self.study_id = study_id
        self.age = age
        self.sex = sex


class SetUp(injector.Module):
    # abusing Session a bit; this really provides a subclass, not an instance, of Session
    @provides((sqlalchemy.orm.session.Session, CONFIG_SECTION))
    @inject(engine=(sqlalchemy.engine.base.Connectable, CONFIG_SECTION))
    def redcap_sessionmaker(self, engine):
        return sqlalchemy.orm.sessionmaker(engine)


class ModuleHelper(object):
    @classmethod
    def mods(cls, ini):
        return [cls(ini), SetUp()]

    @classmethod
    def make(cls, ini, what=(sqlalchemy.orm.session.Session, CONFIG_SECTION)):
        return injector.Injector(cls.mods(ini)).get(what)
    

class Mock(injector.Module, ModuleHelper):
    def __init__(self, ini):
        injector.Module.__init__(self)

    @singleton
    @provides((sqlalchemy.engine.base.Connectable, CONFIG_SECTION))
    def redcap_datasource(self):
        import logging  #@@ lazy
        log = logging.getLogger(__name__)
        #salog = logging.getLogger('sqlalchemy.engine.base.Engine')
        #salog.setLevel(logging.INFO)
        log.debug('redcap create_engine: again?')
        e = sqlalchemy.create_engine('sqlite://')
        redcap_data.create(e)
        return e


class RunTime(injector.Module, ModuleHelper):
    def __init__(self, ini):
        injector.Module.__init__(self)
        self._ini = ini

    def configure(self, binder):
        def bind_options(names, section):
            rt = config.RuntimeOptions(names)
            rt.load(self._ini, section)
            binder.bind((config.Options, section), rt)

        #@@todo: rename sid to database (check sqlalchemy docs 1st)
        bind_options('user password host port database engine'.split(), CONFIG_SECTION)

    @singleton
    @provides((sqlalchemy.engine.base.Connectable, CONFIG_SECTION))
    @inject(rt=(config.Options, CONFIG_SECTION))
    def redcap_datasource(self, rt, driver='mysql+mysqldb'):
        # support sqlite3 driver?
        u = (rt.engine if rt.engine else
             sqlalchemy.engine.url.URL(driver, rt.user, rt.password,
                                       rt.host, rt.port, rt.database))

        # inverted w.r.t. object capability style, no?
        return sqlalchemy.create_engine(u)


if __name__ == '__main__':
    import sys, pprint

    ini = 'integration-test.ini'
    sm = RunTime.make(ini)
    print sm().query(redcap_data).slice(1, 10)
    print sm().query(redcap_data).slice(1, 10).all()

    rt = config.RuntimeOptions('project_id')
    rt.load(ini, 'oversight_survey')  # peeking
    ans = sm().execute(select([redcap_data.c.field_name], distinct=True
                              ).where(redcap_data.c.project_id ==
                                      rt.project_id))
    pprint.pprint(ans.fetchall())
