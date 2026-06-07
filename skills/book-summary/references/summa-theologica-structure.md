# Summa Theologica — Structural Map

**Author:** St. Thomas Aquinas (1225-1274)
**Translator:** Fathers of the English Dominican Province
**Source:** documentacatholicaomnia.eu (direct PDF link)
**Pages:** 9,453
**RAG chunks:** 6,886 (500 word chunks, 100 overlap)
**PDF filename:** Summa_Theologica_Thomas_Aquinas.pdf

## PDF Origin

This PDF is an HTML-to-PDF conversion from documentacatholicaomnia.eu. Key characteristics:
- No reliable page numbers for `pdftotext -f/-l`
- Structural markers use form-feed + uppercase name: `\fPRIMAPARS:`, `\fPRIMASECUNDAE:`, etc.
- Full TOC/index appears first (lines 1-2794 in full-text export), then actual content
- Content starts at `\fPRIMAPARS: PROLOGUE` marker

## Five Major Parts

### 1. PRIMA PARS (First Part)
- **Lines:** 2795–5179 (full text)
- **Questions:** 1–119
- **Major Treatises:**
  - Sacred Doctrine (Q. 1)
  - The One God — existence, attributes, simplicity, perfection, goodness, infinity, eternity, unity, knowledge, will, love, justice, mercy, providence, predestination, power, beatitude (Q. 2–26)
  - The Trinity — procession, relations, persons (Father, Son, Holy Ghost), equality, mission (Q. 27–43)
  - Creation — first cause, beginning of duration, distinction of things, evil (Q. 44–49)
  - Angels — substance, knowledge, will, production, perfection, malice, punishment (Q. 50–64)
  - Work of the Six Days (Hexaemeron) — light, firmament, waters, plants, heavenly bodies, birds/fishes, animals, man (Q. 65–74)
  - Man — soul, body, intellect, will, knowledge, original state, paradise (Q. 75–102)
  - Government of Creatures — divine government, preservation, change, fate, human action, propagation (Q. 103–119)

### 2. PRIMA SECUNDAE (First Part of the Second Part)
- **Lines:** 5180–7610
- **Questions:** 1–114
- **Major Treatises:**
  - Last End (Beatitude) — man's last end, happiness, what it consists in, attainment (Q. 1–5)
  - Human Acts — voluntariness, circumstances, will, intention, choice, consent, command, good/evil (Q. 6–21)
  - Passions — love, hatred, desire, pleasure, pain, fear, anger (Q. 22–48)
  - Habits — substance, cause, increase, corruption (Q. 49–54)
  - Virtues — definition, subject, intellectual, moral, cardinal, gifts, beatitudes, fruits (Q. 55–70)
  - Vices and Sin — essence, distinction, original sin, effects (Q. 71–89)
  - Law — essence, kinds (eternal, natural, human, divine), Old Law, New Law (Q. 90–108)
  - Grace — necessity, essence, causes, justification, merit (Q. 109–114)

### 3. SECUNDA SECUNDAE (Second Part of the Second Part)
- **Lines:** 7611–11355
- **Questions:** 1–189
- **Major Treatises:**
  - Faith — nature, act, habit, virtues connected (Q. 1–16)
  - Hope and Fear (Q. 17–22)
  - Charity — nature, object, act, order, vices opposed (hatred, sloth, envy, discord, schism, war) (Q. 23–46)
  - Prudence — nature, parts, gift of counsel (Q. 47–56)
  - Justice — nature, parts (commutative, distributive), restitution, judgment (Q. 57–80)
  - Religion — devotion, prayer, adoration, sacrifice, vows, superstition, irreligion (Q. 81–100)
  - Sins against Justice — murder, theft, injustice, lying, fraud, usury (Q. 64–79)
  - Fortitude — martyrdom, fear, daring, anger (Q. 123–140)
  - Temperance — modesty, abstinence, fasting, sobriety, chastity, virginity, lust, gluttony (Q. 141–170)
  - Prophecy, Rapture, Active vs Contemplative Life, States of Life (Q. 171–189)

### 4. TERTIA PARS (Third Part)
- **Lines:** 11356–13542
- **Questions:** 1–90
- **Major Treatises:**
  - Incarnation — fitness, mode of union, Christ's grace, knowledge, power, defects (Q. 1–26)
  - Life of Christ — conception, birth, baptism, temptation, passion, death, resurrection, ascension, judgment (Q. 27–59)
  - Sacraments — nature, necessity, effect, Baptism, Confirmation, Eucharist (Q. 60–90)

### 5. SUPPLEMENTUM (Supplement)
- **Lines:** 13543–247820 (very long — includes extensive Scriptural commentary)
- **Questions:** 1–99
- **Major Treatises:**
  - Penance — contrition, confession, satisfaction, indulgences (Q. 1–25)
  - Extreme Unction (Q. 26–33)
  - Holy Orders and Matrimony (Q. 34–68)
  - Purgatory, Resurrection, Last Judgment, Beatific Vision, Damned (Q. 69–99)

## Structural Markers (for grep)

```bash
# Export full text
pdftotext ~/RAG/books/Summa_Theologica_Thomas_Aquinas.pdf /tmp/summa_full.txt

# Find content part boundaries
grep -n $'\\fPRIMAPARS:\\|\\fPRIMASECUNDAE:\\|\\fSECUNDASECUNDAE:\\|\\fTERTIAPARS:\\|\\fSUPPLEMENTUM:' /tmp/summa_full.txt

# Find individual Questions within a Part
grep -n "QUESTION [0-9]" /tmp/summa_full.txt | head -50

# Read specific Question content
sed -n '<start_line>,<end_line>p' /tmp/summa_full.txt
```

## Query Strategy

For a book this large, batch_query with 17 queries (one per major treatise) is appropriate. Do NOT query every individual Question (119+114+189+90+99 = 611 Questions) — that would take days. Level at Part/Treatise granularity.

RAG contamination risk for Summa: Questions share vocabulary heavily (all treat divine/moral topics), so vector search may return chunks from the wrong Part for similar-sounding queries. Cross-check results with pdftotext range reads before writing summary.
