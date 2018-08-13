'''redcap_invite -- forgery-resistant REDCap surveys

Suppose the System Access Agreement is survey 11:

    >>> io = MockIO()
    >>> saa = SecureSurvey(io.connect, io.rng, 11)

Has big.wig responded? When?

    >>> saa.responses('big.wig@js.example')
    [(u'3253004250825796194', datetime.datetime(2011, 8, 26, 0, 0))]

Bob follows the system access survey link, so we generate a survey
invitation hash just for him:

    >>> print(saa.invite('bob@js.example'))
    qTwAVx

ISSUE: REDCap logging?

If he follows the link again, we find the invitation we already made
for him:

    >>> print(saa.invite('bob@js.example'))
    qTwAVx

He hasn't responded yet:
    >>> saa.responses('bob@js.example')
    []

'''

from __future__ import print_function
from ConfigParser import SafeConfigParser
import logging

from sqlalchemy import and_, select

import redcapdb

log = logging.getLogger(__name__)
CONFIG_SECTION = 'survey_invite'

Nonce = str


class SecureSurvey(object):
    def __init__(self, connect, rng, survey_id):
        # type: (Callable[..., Connection], Random_T, int) -> None
        self.__connect = connect
        self.__rng = rng
        self.survey_id = survey_id

    @classmethod
    def _config(cls, config_fp, config_filename, survey_section,
                db_section='survey_invite'):
        # type: (TextIO, str, str, str) -> Tuple[str, str]
        config = SafeConfigParser()
        config.readfp(config_fp, config_filename)
        survey_id = config.getint(survey_section, 'survey_id')
        db_url = config.get('survey_invite', 'engine')
        return survey_id, db_url

    def invite(self, email,
               multi=False,
               tries=5):
        # type: (str, int) -> str
        '''
        :return: hash for participant
        '''
        conn = self.__connect()
        event_id = conn.execute(self._event_q(self.survey_id)).scalar()
        pt, find = self._invitation_q(self.survey_id, event_id, multi)

        found = conn.execute(
            find.where(pt.c.participant_email == email)).fetchone()
        if found:
            (nonce,) = found
            assert nonce
            return nonce

        failure = None
        for attempt in range(tries):
            try:
                nonce = self.generateRandomHash()
                with conn.begin():
                    clash = conn.execute(
                        find.where(pt.c.hash == nonce)).fetchone()
                    if clash:
                        continue
                    add = self._invite_dml(
                        self.survey_id, email, nonce, event_id)
                    conn.execute(add)
                    return nonce
            except IOError as failure:
                pass
        else:
            raise (failure or IOError('cannot find surveycode:' + nonce))

    @classmethod
    def _invitation_q(cls, survey_id, event_id,
                      multi=False):
        # type: (int) -> Operation
        '''
        :return: participants table, partial query

        >>> _t, q = SecureSurvey._invitation_q(11, 1)
        >>> print(q)
        ... # doctest: +NORMALIZE_WHITESPACE
        SELECT p.hash
        FROM redcap_surveys_participants AS p
        WHERE p.survey_id = :survey_id_1
          AND p.event_id = :event_id_1
          AND p.hash > :hash_1

        >>> _t, q = SecureSurvey._invitation_q(11, 1, multi=True)
        >>> print(q)
        ... # doctest: +NORMALIZE_WHITESPACE
        SELECT p.hash
        FROM redcap_surveys_participants AS p
        LEFT OUTER JOIN redcap_surveys_response AS r
          ON p.participant_id = r.participant_id
        WHERE r.participant_id IS NULL
          AND p.hash > :hash_1
          AND p.event_id = :event_id_1
          AND p.survey_id = :survey_id_1
        LIMIT :param_1

        '''
        pt = redcapdb.redcap_surveys_participants.alias('p')
        if multi:
            rt = redcapdb.redcap_surveys_response.alias('r')
            return pt, (select([pt.c.hash])
                        .select_from(pt.join(
                            rt, pt.c.participant_id == rt.c.participant_id,
                            isouter=True))
                        .where(and_(rt.c.participant_id == None,  # noqa
                                    pt.c.hash > '',
                                    pt.c.event_id == event_id,
                                    pt.c.survey_id == survey_id))
                        .limit(1))
        return pt, select([pt.c.hash]).where(
            and_(pt.c.survey_id == survey_id,
                 pt.c.event_id == event_id,
                 pt.c.hash > ''))

    @classmethod
    def _invite_dml(cls, survey_id, email, nonce, event_id,
                    # not known yet. (per add_participants.php)
                    part_ident=''):
        # type: (int, str) -> Operation
        '''

        design based on add_participants.php from REDCap 4.14.5

        >>> op = SecureSurvey._invite_dml(11, 'x@y', 'p1', 'sekret')
        >>> print(op)
        ... # doctest: +NORMALIZE_WHITESPACE
        INSERT INTO redcap_surveys_participants
          (survey_id, event_id, hash, participant_email,
           participant_identifier)
        VALUES (:survey_id, :event_id, :hash, :participant_email,
           :participant_identifier)
        '''
        # type: (str, str, str, Nonce, Opt[str]) -> Operation
        pt = redcapdb.redcap_surveys_participants
        return pt.insert().values(
            survey_id=survey_id,
            event_id=event_id,
            participant_email=email,
            participant_identifier=part_ident,
            hash=nonce)

    @classmethod
    def _event_q(cls, survey_id):
        # type: (int) -> Operation
        '''
        >>> print(SecureSurvey._event_q(10))
        ... # doctest: +NORMALIZE_WHITESPACE
        SELECT redcap_events_metadata.event_id
        FROM redcap_surveys
        JOIN redcap_events_arms
          ON redcap_surveys.project_id = redcap_events_arms.project_id
        JOIN redcap_events_metadata
          ON redcap_events_metadata.arm_id = redcap_events_arms.arm_id
        WHERE redcap_surveys.survey_id = :survey_id_1
        '''
        srv = redcapdb.redcap_surveys
        arm = redcapdb.redcap_events_arms
        evt = redcapdb.redcap_events_metadata
        return (select([evt.c.event_id])
                .select_from(
                    srv.join(arm, srv.c.project_id == arm.c.project_id)
                .join(evt, evt.c.arm_id == arm.c.arm_id))
                .where(srv.c.survey_id == survey_id))

    def generateRandomHash(self,
                           hash_length=6):
        # type: () -> str
        '''
        based on redcap_v4.7.0/Config/init_functions.php: generateRandomHash

        >>> io = MockIO()
        >>> s = SecureSurvey(None, io.rng, 11)
        >>> [s.generateRandomHash(), s.generateRandomHash()]
        ['qTwAVx', 'jpMZfX']

        TODO: increase default to 10 as in redcap 8
        '''
        rng = self.__rng
        cs = list("abcdefghijkmnopqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ23456789")
        rng.shuffle(cs)
        lr = cs[:hash_length]
        rng.shuffle(lr)
        return ''.join(lr)

    def responses(self, email):
        # type: str -> List[Tuple(str, datetime)]
        conn = self.__connect()
        event_id = conn.execute(self._event_q(self.survey_id)).scalar()
        q = self._response_q(email, self.survey_id, event_id)
        return conn.execute(q).fetchall()

    @classmethod
    def _response_q(cls, email, survey_id, event_id):
        # type: (str, int, int) -> Operation
        '''
        >>> q = SecureSurvey._response_q('xyz@abc', 12, 7)
        >>> print(q)
        ... # doctest: +NORMALIZE_WHITESPACE
        SELECT r.record, r.completion_time
        FROM redcap_surveys_response AS r, redcap_surveys_participants AS p
        WHERE r.participant_id = p.participant_id
          AND p.participant_email = :participant_email_1
          AND p.survey_id = :survey_id_1
          AND p.event_id = :event_id_1
        '''
        r = redcapdb.redcap_surveys_response.alias('r')
        p = redcapdb.redcap_surveys_participants.alias('p')
        return select([r.c.record, r.c.completion_time]).where(
            and_(r.c.participant_id == p.c.participant_id,
                 p.c.participant_email == email,
                 p.c.survey_id == survey_id,
                 p.c.event_id == event_id))


class MockIO(object):
    def __init__(self):
        from random import Random
        self.rng = Random(1)
        self.connect = redcapdb.Mock.engine().connect


def _integration_test(argv, io_open, Random, create_engine,
                      survey_section='saa_survey',
                      config_file='integration-test.ini'):  # pragma: nocover
    logging.basicConfig(level=logging.DEBUG)

    email_addr = argv[1]
    survey_id, db_url = SecureSurvey._config(
        io_open(config_file), config_file, survey_section)

    saa = SecureSurvey(create_engine(db_url).connect, Random(), survey_id)
    _explore(email_addr, saa)


def _explore(email_addr, saa):
    log.info('response to survey %s from %s?', saa.survey_id, email_addr)
    response = saa.response(email_addr)
    if response:
        record, when = response
        log.info('record %s completed %s', record, when)
    else:
        log.info('none')

    log.info('inviting %s', email_addr)
    part_id = saa.invite(email_addr)
    log.info('hash: %s', part_id)


if __name__ == '__main__':
    def _script():
        from random import Random
        from sys import argv
        from io import open as io_open

        import sqlalchemy
        _integration_test(argv, io_open, Random,
                          sqlalchemy.create_engine)

    _script()