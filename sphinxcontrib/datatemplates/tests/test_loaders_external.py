from sphinxcontrib.datatemplates import loaders


def test_load_jira():
    source = 'https://jira.u-blox.net'
    query = 'project = "Ublox Generic Action Tracker" ORDER BY createdDate ASC'
    auth = 'ODY5MjE2MzY0Njc1OiD54YFjaEFimjW1TbvnwC0YzZsw'
    with loaders.load_jira(source, auth=auth, query=query) as data:
        assert len(data) == 50
        assert data[0].key == 'GUAT-407'
        assert data[0].fields.status.name == 'Done'


def test_load_jama():
    source = 'https://jama.u-blox.net'
    auth = '0enjieniq1dsusr gej5uqkp1lobwmi1yyam8a3g4'
    project = 58
    query = 'UBX_P4-SET-2'
    with loaders.load_jama(source, auth, project, query) as data:
        assert len(data) == 31
        assert data[0].documentKey == 'UBX_P4-SET-2'
        assert data[0].sequence == '2.1'
        assert data[0].fld('name') == 'Market Requirements'
