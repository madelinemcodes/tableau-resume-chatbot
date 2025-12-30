# Frontend Testing Guide

Now that you have `chatbot.html`, let's test it and understand how it works!

---

## Step 1: Copy chatbot.html to Your Project

Download `chatbot.html` from my outputs and put it in:

```
tableau-resume-chatbot/static/chatbot.html
```

**Verify it's there:**
```bash
cd ~/Desktop/tableau-resume-chatbot
ls static/
```

You should see:
```
chatbot.html
```

---

## Step 2: Make Sure Flask Server is Running

In your **first terminal** (the one where Flask runs):

```bash
cd ~/Desktop/tableau-resume-chatbot
source venv/bin/activate
python app.py
```

You should see:
```
🚀 Starting Flask server...
 * Running on http://127.0.0.1:5000
```

**Keep this terminal open and running!**

---

## Step 3: Open the Chatbot in Your Browser

Open your web browser and go to:

```
http://localhost:5000
```

**What you should see:**

A beautiful chat interface with:
- Purple gradient background
- White chat box in the center
- Title: "💬 Ask About Madeline's Qualifications"
- Four suggestion buttons
- Empty chat area
- Input box at the bottom
- "Ask" button

---

## Step 4: Test the Welcome Message

When the page loads, you should immediately see a message from Claude:

```
Hi! I'm an AI assistant trained on Madeline's resume. 
Ask me anything about her experience, skills, projects, 
or qualifications for your role.
```

**This message appears automatically** - it's defined in the JavaScript at the bottom of the HTML file.

---

## Step 5: Test with a Suggestion Button

Click on one of the suggestion buttons, like:
**"How experienced is Madeline with Tableau?"**

**What should happen:**

1. The question appears in a **blue bubble** on the right
2. Three **bouncing dots** appear (typing indicator)
3. After 2-5 seconds, Claude's answer appears in a **gray bubble** on the left
4. The input box clears and is ready for another question

**What you're seeing happen behind the scenes:**

```
1. JavaScript captures your click
   ↓
2. Fills the input box with the question
   ↓
3. Calls sendQuestion() function
   ↓
4. sendQuestion() sends POST request to http://localhost:5000/api/chat
   ↓
5. Flask receives it, asks Claude
   ↓
6. Claude responds with answer
   ↓
7. Flask sends response back
   ↓
8. JavaScript receives the JSON
   ↓
9. JavaScript calls addMessage() to display it
   ↓
10. You see the answer!
```

---

## Step 6: Test by Typing Your Own Question

In the input box at the bottom, type:
```
What cost savings has she delivered?
```

Press **Enter** or click the **Ask** button.

**What should happen:**

Same process as before - your question appears in blue, then Claude's answer appears in gray.

---

## Step 7: Test Multiple Questions

Ask 3-4 questions in a row:

1. "What cost savings has she delivered?"
2. "Can she work with Python?"
3. "Does she have Snowflake experience?"
4. "Has she managed a team?"

**What to observe:**

- Messages stack vertically
- The chat area scrolls automatically
- Each question/answer pair is clearly visible
- The typing indicator appears each time
- Button disables while loading (can't click twice)

---

## Understanding What You See

### The Message Bubbles

**Blue bubbles (right side):**
- These are YOUR questions (the recruiter)
- Created with CSS class `.recruiter`
- `margin-left: auto` pushes them to the right

**Gray bubbles (left side):**
- These are CLAUDE'S responses
- Created with CSS class `.claude`
- Naturally align to the left

### The Typing Indicator

Those three bouncing dots appear when:
- JavaScript calls `showTypingIndicator()`
- Which adds class `.active` to the typing indicator
- CSS `.active` class changes `display: none` to `display: block`

**Why this matters:**
- Gives user feedback ("something is happening")
- Makes the experience feel more natural
- Better UX than just waiting with no indication

### The Smooth Animations

Notice how messages **fade in** smoothly?

That's this CSS:
```css
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
```

It starts invisible and slightly below, then fades in and moves up. Takes 0.3 seconds.

---

## Testing Checklist

Go through this list:

- [ ] Page loads with welcome message
- [ ] Can click suggestion buttons and get responses
- [ ] Can type questions manually and get responses
- [ ] Can press Enter to send questions
- [ ] Messages appear in correct colors (blue for you, gray for Claude)
- [ ] Typing indicator appears while waiting
- [ ] Button says "Thinking..." while processing
- [ ] Chat area scrolls automatically to show new messages
- [ ] Multiple questions work in a row
- [ ] No errors in browser console (press F12 to open)

---

## Debugging: If Something Doesn't Work

### Issue 1: Page Shows "Cannot GET /"

**Problem:** Flask server not running or crashed

**Fix:**
- Check terminal where you ran `python app.py`
- Is it still running?
- Any errors shown?
- Restart it if needed

---

### Issue 2: Clicking "Ask" Does Nothing

**Problem:** JavaScript error or backend not reachable

**Fix:**
1. Open browser console (F12 or right-click → Inspect → Console)
2. Look for red error messages
3. Common issues:
   - "Failed to fetch" → Backend not running
   - "CORS error" → flask-cors not installed
   - "404 error" → API_URL is wrong

**Check API_URL in the HTML:**
```javascript
const API_URL = 'http://localhost:5000/api/chat';
```

Should match where your Flask server is running.

---

### Issue 3: Getting Error Messages Instead of Answers

**Problem:** Backend is running but Claude API is failing

**Fix:**
1. Check Flask terminal for error messages
2. Common issues:
   - API key invalid → Check `.env` file
   - No credits → Add credits to Anthropic account
   - Network error → Check internet connection

---

### Issue 4: Answers Take Forever

**Problem:** Claude API is slow or timing out

**What's normal:**
- 2-5 seconds is normal
- First request might be slower (cold start)
- Very long questions take longer

**If it's > 10 seconds:**
- Check Flask logs for errors
- Check Anthropic console for rate limits
- Try a shorter question

---

## View Source: Understanding the Code

Open the chatbot in your browser, then:
1. Right-click anywhere on the page
2. Click "View Page Source"

You'll see the **exact HTML we created**, but your browser has:
- Parsed the HTML into elements
- Applied the CSS styling
- Executed the JavaScript
- Made it interactive

**This is what web development is** - writing text files that browsers turn into interactive applications!

---

## Check Browser Console

Press **F12** (or right-click → Inspect → Console)

After asking a question, you should see:
```
Token usage: {input_tokens: 3247, output_tokens: 156}
```

This is from this line in the JavaScript:
```javascript
console.log('Token usage:', data.usage);
```

**Why this is useful:**
- You can monitor costs in real-time
- Debug issues
- See what's actually happening

---

## Customization Ideas (For Later)

Once it's working, you could customize:

### Change Colors
In the CSS, find:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

Change the hex colors to your brand colors!

### Change Suggestion Questions
In the HTML, find:
```html
<div class="suggestion" onclick="askQuestion('...')">
```

Change the questions to ones more relevant to your target roles!

### Add More Features
- Email button after conversations
- Copy answer to clipboard
- Download conversation history
- Add timestamps to messages

---

## Performance Check

After testing, check:

**In Anthropic Console** (https://console.anthropic.com/settings/usage):
- How many requests?
- How much did it cost?
- Token usage?

**Expected for 5-10 test questions:**
- ~10 requests
- ~$0.10-0.20 spent
- Normal!

---

## Success Criteria

Your frontend is working if:

✅ Page loads with no errors
✅ Welcome message appears automatically
✅ Clicking suggestions sends questions
✅ Typing and pressing Enter works
✅ Claude's responses appear in gray bubbles
✅ Typing indicator shows while waiting
✅ Multiple questions work in sequence
✅ No console errors (F12)
✅ Responses are accurate and cite your resume data

---

## Next Steps

Once your frontend is working locally, we'll:

1. **Test the complete flow** - Make sure everything works end-to-end
2. **Deploy to production** - Make it accessible online (not just localhost)
3. **Embed in Tableau** - Add it to your Tableau Public dashboard

---

## You're Almost There!

You now have:
- ✅ Working backend API
- ✅ Beautiful frontend interface
- ✅ Complete chatbot application running locally

The next step is deploying this so it works on the internet (not just your computer), which will let you embed it in Tableau Public!
