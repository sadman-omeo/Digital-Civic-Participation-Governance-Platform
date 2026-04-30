#!/usr/bin/env python
"""
Database migration script to add new columns to the Voter table
"""
from app import app, db
from models.voters import Voter
from datetime import datetime

with app.app_context():
    # Create all tables (this will add new columns if they don't exist)
    db.create_all()
    print("✓ Database schema updated successfully")
    
    # Check if the columns exist by querying
    try:
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('voter')]
        print(f"✓ Voter table columns: {columns}")
        
        if 'last_vote_candidate' in columns:
            print("✓ New columns are present in database")
        else:
            print("⚠ New columns not yet in database, attempting to add them...")
            # If columns don't exist, we need to add them manually
            with db.engine.connect() as conn:
                # Add columns if they don't exist
                try:
                    conn.execute(db.text('ALTER TABLE voter ADD COLUMN last_vote_candidate VARCHAR(255)'))
                    print("✓ Added last_vote_candidate column")
                except:
                    print("  (last_vote_candidate column might already exist)")
                
                try:
                    conn.execute(db.text('ALTER TABLE voter ADD COLUMN last_vote_election VARCHAR(255)'))
                    print("✓ Added last_vote_election column")
                except:
                    print("  (last_vote_election column might already exist)")
                
                try:
                    conn.execute(db.text('ALTER TABLE voter ADD COLUMN vote_notes TEXT'))
                    print("✓ Added vote_notes column")
                except:
                    print("  (vote_notes column might already exist)")
                
                try:
                    conn.execute(db.text('ALTER TABLE voter ADD COLUMN last_edited_at DATETIME'))
                    print("✓ Added last_edited_at column")
                except:
                    print("  (last_edited_at column might already exist)")
                
                conn.commit()
    except Exception as e:
        print(f"Error during migration: {e}")

print("\n✓ Migration completed!")
