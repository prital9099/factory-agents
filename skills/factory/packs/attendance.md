# Pack: attendance register (preschool or school)

Used by spec-requirements in draft mode. Each line is a question with its recommended
default, in plain words. The user can change any of them. These come from a finished job
(a preschool attendance app); change them if the new feature differs.

1. [you] Goal: replace the paper register. Success: the admin gets the monthly report
   on screen in one click.
2. [you] Platform: a website that also works well on phones. No separate phone apps.
3. [you] Stack: no preference, propose a simple one (the last job used React with
   TypeScript, FastAPI and PostgreSQL). Hosting: decide later, run locally for now.
4. [you] Size: one school, a few classes of about 15 children, one teacher per class.
5. [you] Roles: admin, teacher, parent, plus a stand-in teacher for one day.
6. [you] Accounts: admin creates every account and sets or resets passwords. Sign in with
   email and password. The app sends no emails or messages.
7. [you] Record per child per day: present or absent only. No arrival, departure or pickup
   times. Session hours (for example 9:00 to 12:30) are shown as information only.
8. [you] Default: every child starts as present. The teacher marks only the absent ones
   and taps Save every school day, even if nobody is absent.
9. [you] Confirmation: tapping Save opens a box "Are you sure you want to save
   attendance?" with Confirm and Cancel. Cancel keeps the marks on screen, not saved. The
   box appears on every attendance save, not on other admin forms. Decide later whether
   Esc or a tap outside closes it.
10. [you] A day nobody saved shows "Not marked" to everyone and is left out of totals.
11. [you] A teacher can save a missed day for any day within 3 years. A stand-in can
    save only their assigned day. Admin can save any day.
12. [you] Corrections: a teacher can correct a saved day only on the day it was saved.
    Admin can correct any time.
13. [you] Audit: ask this plainly. Recommended: keep a hidden record of every
    correction that no screen shows. (The last job chose no record at all after being
    warned that this removes accountability for children's data.)
14. [you] Calendar: Saturday and Sunday off, admin adds other holidays by date.
15. [you] Go-live date set by admin. Days before it are not counted. If it moves
    later, earlier saved days are hidden and kept, not deleted.
16. [you] Links: a child can have several parent accounts and a parent several children.
17. [you] Parent screen: month list plus a day picker, per child, from the go-live date
    (or the child's added date) up to today. No future dates.
18. [you] Reports: on screen only, per class: days present, days absent, attendance %
    (present divided by present plus absent, rounded). Admin sees all classes, a teacher
    sees their own, a parent sees their child.
19. [you] Privacy and keeping data: English only; follow the data protection law of
    your country (the last job followed India's DPDP Act principles); keep records 3
    years, then the admin deletes them by hand; no child photos.
20. [you] Out of scope: fees and billing, activity reports, chat, several schools, offline
    use, notifications, report export, pickup recording.
21. [you] Not blocking (decide at design time): moving children up a class at year end; a
    child leaving mid-year.
22. [you] Deliverables: please attach a sample test-case spreadsheet if you have one
    (layout, columns, id style).
