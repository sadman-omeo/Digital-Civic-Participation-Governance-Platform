#!/usr/bin/env python
"""
Generate SECRET_KEY for production
Run this and copy the output to Vercel environment variables
"""
import secrets

if __name__ == "__main__":
    secret_key = secrets.token_hex(32)
    print("=" * 60)
    print("GENERATED SECRET_KEY FOR PRODUCTION")
    print("=" * 60)
    print(f"\n{secret_key}\n")
    print("=" * 60)
    print("Copy this value to Vercel:")
    print("  Settings → Environment Variables → Add 'SECRET_KEY'")
    print("=" * 60)
