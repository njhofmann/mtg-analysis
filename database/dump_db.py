import subprocess as sbp
"""Module for creating a backup of the database based off of the given params"""


def create_dump(db_name, backup_name, user):
    """
    Creates a text dump of the given database as the given user, with the given file name. Used to create backups of
    the desired database. Prints any errors that may occur during process.
    :param db_name: name of the database to dump
    :param backup_name: name of created dump file
    :param user: user to login into database as
    :return: None
    """
    command = ['pg_dump', '-d', db_name, '-f', backup_name, '-U', user]
    process = sbp.Popen(args=command, stdout=sbp.PIPE, stderr=sbp.PIPE)
    process.wait()
    out, err = process.communicate()

    out = out.decode('utf-8')
    err = err.decode('utf-8')

    if process.returncode != 0:
        print(err)
    else:
        print(out)


if __name__ == '__main__':
    create_dump('mtg_analysis', 'db_backup.txt', 'postgres')