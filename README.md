# Mass Booklet Generator 📖✨

Welcome! This friendly tool helps you quickly and easily create beautiful, ready-to-print Catholic Mass booklets in both English and Vietnamese. Say goodbye to manual copy-pasting and formatting headaches!

## What It Does 🌟

* **Automatic Scripture Fetching:** Pulls the official daily scripture readings automatically (English from [USCCB](https://bible.usccb.org/) and Vietnamese from [Thanh Linh](https://thanhlinh.net/)) for any date you choose.
* **Custom Hymns & Details:** Seamlessly integrates your opening hymns, offertory songs, communion music, and church/organization name.
* **Instant Word Documents:** Generates a polished, professionally formatted Microsoft Word document (`.docx`) saved right to your folder, ready for printing or final edits.

---

## ⚠️ Important Note on Quality

Technology is never perfect. The automated web scrapers can (and will!) miss formatting nuancess or layout updates on the source websites. **Please carefully review, proofread, and reformat every generated booklet as needed before printing or using it for Mass.**

---

## Folder Guide 🗂️

* **`config/`**: Where your settings live. You can set up single dates or batch lists of dates and customize your hymns.
* **`output/`**: Where your freshly generated Mass booklets appear like magic!
* **`experiments/`**: Advanced cluster folder. (Note: Most users should stick to single runs; this was primarily built for bulk QA testing across a wide range of dates.)
* **`src/`**: The behind-the-scenes engine that does all the heavy lifting.

---

## How to Use It 🚀

### 0. Customize Your Settings (Before You Run!)
Before running either script, make sure to update your settings inside the **`config/`** folder to match your event and preferences:
* **`date`**: Enter your target Mass date in `MMDDYY` format.
* **`organization`**: Type the name of your church, community, or group.
* **`event_name`**: Specify the name of the special Mass or event (e.g., Sunday Mass, Feast Day).
* **`hymns`**: Customize your titles, choruses, and verses for the opening, offertory, communion, and closing/recessional songs.
* **`reading1`, `psalm`, `reading2`, `alleluia`, `gospel`**: Set your preferred languages (`"eng"` for USCCB English readings or `"viet"` for Thanh Linh Vietnamese readings) and choose your option index if there are multiple choices.

### 1. Create a Single Booklet (Recommended!)

For everyday use, simply run a single generation:

```bash
./single_run.sh
```

Your finished document will pop right into the **`output/`** folder!

### 2. Batch Mode (Advanced HPC Users)

If you have access to a High-Performance Computing (HPC) cluster, you can run bulk document generations across multiple dates using:

```bash
./experiment_run.sh
```

However, this configuration is provided primarily as an option for quality assurance. The experimental run was built by the developers to perform quality assurance checks across many dates, and the main recommendation for everyday use is to stick with the single run script. 

---

## Thank You 🙏

Thank you for using this tool, and THANK YOU for taking the care to ensuring a beautiful and sacred Mass. Please do not hesitate to email me with questions or comments! I would LOVE to hear how you are using this tool, and listen to your insights.

*When you leave the Mass, live the Mass,*
<br>
<p style="margin: 0; font-family: sans-serif; font-size: 14px; color: #111;"><b>Tr. John Paul II Nguyễn Dovan Simon</b></p>
<p style="margin: 0; font-family: sans-serif; font-size: 13px; color: #555;"><a href="mailto:simon.nguyen1@veym.net" style="color: #0056b3; text-decoration: underline;">simon.nguyen1@veym.net</a></p>
This website is a personal project and not endorsed by VEYM.

<!-- <p style="margin: 2px 0 2px 0; font-family: sans-serif; font-size: 13px; color: #444;">Ủy Viên Phụng Vụ Ban Chấp Hành Trung Ương 2026-2030</p> -->
