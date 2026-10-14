# Privacy and data handling

This describes what the code does today. It is not a legal privacy policy
and does not claim compliance with any law or standard (for example FERPA).
Anything planned but not built is listed under "Not done yet".

## What the tool is

A tool that runs on one staff member's computer. It has no user accounts, no
login, no server, no analytics, and no AI or other external service at run
time. Students do not use it; staff run it on exported CSV files.

## What data it reads, and why

| Data | Where it comes from | Why it is needed |
|---|---|---|
| `student_id` | Students CSV | Tells students apart in the results |
| `name` | Students CSV | Only so staff can read the results. Matching does not use it. |
| `skills`, `completed_courses` | Students CSV | The input to matching |
| `opportunity_id`, `partner_org`, `title`, `required_skills` | Opportunities CSV | The other side of the match (not personal data) |
| Course list | `data/courses.csv` | Course recommendations and timelines (not personal data) |

Nothing else is collected. The only student data in this repository is the
sample in `data/sample_students.csv`. No real NPower data has been loaded
yet.

## Where data goes and how long it stays

**Streamlit app (`streamlit run app.py`)**

- Uploaded CSVs and the database built from them are written to a temporary
  folder and deleted as soon as the results are read. The app does not write
  to `db/` or `output/`. (`tests/test_app.py` checks this for `db/`.)
- Results stay in the app's memory until the browser tab is closed or the
  app is stopped.
- A file the user downloads from the app is an ordinary file on their
  computer. The tool cannot delete it.
- Streamlit's usage statistics are turned off in `.streamlit/config.toml`.
  That file only applies when the app is started from the project folder.

**Command line (`python -m src.pipeline`)**

- Writes `db/skills_match.db` and three CSVs in `output/`. These contain
  student names and skills.
- They stay there until the next run overwrites them or someone deletes
  them. There is no automatic expiry.
- Both locations are git-ignored, and so is everything in `data/` except the
  sample files, so real records are not committed by accident.

## Deleting student data

There are no accounts, so there is no account deletion. To remove student
data from a machine, delete:

1. `db/skills_match.db`
2. everything in `output/` except `.gitkeep`
3. any real CSV placed in `data/`
4. any results CSV downloaded from the app

To remove one student, delete their row from the source CSV, delete the
files above, and run again.

## Limits

- Deleting a file does not remove copies in the Recycle Bin, in backups, or
  in a cloud-synced folder. If the project folder is inside OneDrive,
  Dropbox, or similar, `db/` and `output/` are uploaded to that service,
  which goes against NFR-7. Keep the project outside synced folders before
  loading real data.
- The database and output files are not encrypted.
- The app has no login. Anyone who can reach its address can upload files
  and see results in their own session. Run it on your own computer only;
  do not deploy it to a public host.
- Exported CSVs put a `'` in front of any text cell starting with `=`, `+`,
  `-` or `@`, so a spreadsheet does not run it as a formula.

## Not done yet

- A retention period for command-line output, to be agreed with NPower
  before real data arrives
- Deciding whether student names are needed at all, or ids are enough
- Confirming with NPower what student data may be used and where it may be
  stored
