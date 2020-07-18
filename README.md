# Trac username converter

## Use case

- Convert usernames before [migrating from Trac to Redmine](https://github.com/hkato/migrate_from_trac.rake).
- Combine multiple Trac sites into one.
- From local user to LDAP/ActiveDirectory user.
- etc

## Usage

### Export current user list
```sh
$ python trac-username-converter.py export ${TRAC_ENV_PARENT_DIR}/myproj
Export Trac user list... myproj-usermap.csv
Please edit this file: myproj-usermap.csv
```

### Edit username mapping

```sh
$ vi myproj-usermap.csv
```
```diff
 old,new
-hidekato,
-john,
-alison,
+hidekato,hkato
+johnny-rotten,john-lydon
+alison,alison123
```

### Convert username

```sh
$ python trac-username-converter.py convert ${TRAC_ENV_PARENT_DIR}/myproj
Converting... hidekato -> hkato
Converting... johnny-rotten -> john-lydon
Converting... alison -> alison123
```

## Environment

- Trac 1.0.3 (database_version=29)
- Python 3.8.3 (not Trac python version)
