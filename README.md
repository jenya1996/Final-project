# Final Project

-   ncyc - מספר סידורי של מספר המחזור
-   time - זמן בשנים
-   Mwd - מסת הננס הלבן ביחידות של מסות שמש
-   Ms - מסת הכוכב המשני ביחידות של מסות שמש
-   Mdot - קצב הספיחה ביחידות של מסות שמש לשנים
-   a - המרחק בין מרכזי המסות של שני הגופים ביחידות של רדיוסי שמש
-   Porb(hr) - זמן מחזור סיבוב אחד ביחידות של שעות
-   Lirr - בהירות מוקרנת של הכוכב המשני (אנרגיה ליחדות זמן) ביחידות של בהירות שמש
-   Ls - בהירות הכוכב המשני
-   LRD - בהירות משוקללת של הכוכב המשני
-   TeffWD - טמפרטורה אפקטיבית של הננס הלבן בקלווין
-   LWD - בהירות הננס הלבן
-   Lacc - בהירות ספיחה
-   Mboltot - מגניטודה בולומטרית כוללת (מתקשר לבהירות)
-   Rwd - רדיוס הננס הלבן
-   trec - זמן מחזור נובה של המחזור הקודם ביחידות של שנים

## Checklist for File Cleaning and Analysis

### File Cleaning

-   [ ] **Delete the first cycle** from each file (`ncyc`).
-   [ ] **Connect the files**:

    -   [ ] Rearrange the numbering of the cycles to start from `1` and continue sequentially to the end of the data from the second file.
    -   [ ] Rearrange the `time` column to continue seamlessly:
        -   Adjust so that time does not restart with the new file but continues from the previous file.

-   [ ] **Support for multiple files**:
    -   [ ] Ensure functionality works for more than two files, with seamless handling of cycle numbering and time adjustment.

### Data Analysis

-   [ ] **Output parameters for each nova cycle**:
    -   [ ] Calculate and output the following for the **adsorption rate (Mdot)**:
        -   [ ] Initial value
        -   [ ] Final value
        -   [ ] Minimum value
        -   [ ] Average value
    -   [ ] Create a table showing these four parameters for each cycle number.

### Future Steps

-   [ ] Extend parameter outputs:
    -   [ ] Add more parameters to the table.
    -   [ ] Include both directly retrieved and calculated values.
