# The Experiences App 🌟

In the digital plains of our Django application, there lived two kinds of creatures: the People 👥 and the Activities 🎯. This is their story.

## The Law of the Land 📜

The sun rises in the east, and all users can see all activities. This is the way. But the power to change things? That is a different story.

### The Administrators 👑

They are the old guard. The ones who have been here since the beginning. They walk with power:
- They can see all that moves in the kingdom 👀
- They can edit any profile that exists 📝
- They can change any activity that breathes ✨
- And yes, they hold the power of deletion ⚡

### The Facilitators 🎓

The facilitators are like the skilled hunters of the savannah. They have their territory, and in it, they are strong:
- They can see all activities, like everyone else 🌅
- But they can only edit the activities where they are members 🎯
- They cannot delete activities - that power belongs to the administrators alone ⛔
- They are wise in their ways, and they know their boundaries 🌿

### The Regular Users 👤

The regular users are like the wind - they can see everything, but they touch nothing:
- They can view all activities, for knowledge is free 📚
- They cannot edit activities, for that is not their role 🚫
- They can only dream of deletion powers 🌙

## The Sacred Commands 🧙‍♂️

To establish this order, the ancients left us a powerful spell:

```bash
python manage.py setup_groups
```

Run this, and the world aligns itself. The Administrators group is born or renewed, and the permissions flow like water.

## The Dance of Permissions 💃

When a user approaches an activity, the system asks three questions:

1. "Can they see it?" - Yes, always, for all are welcome to look
2. "Can they change it?" - Only if they are:
   - An Administrator (who can change all things)
   - A Facilitator who is part of this activity
3. "Can they delete it?" - Only the Administrators hold this power

## In Practice 🎭

It is a simple dance, really:
- Everyone sees everything 👀
- Administrators rule everything 👑
- Facilitators lead their own activities 🎯
- And peace reigns in the kingdom ☮️

## The End 🌅

And so it goes. The sun sets in the west, and the permissions remain, keeping our digital world in perfect balance.

Remember: With great power comes great responsibility. Use it wisely. 🌟

---
*Written in the style of Hemingway, who never had to deal with Django permissions, but would have appreciated their clarity.* 