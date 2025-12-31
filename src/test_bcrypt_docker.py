
import asyncio
from helpers.password import hash_password, verify_password

async def test_bcrypt():
    password = "password123"
    print(f"Hashing password: {password}")
    try:
        hashed = hash_password(password)
        print(f"Hashed: {hashed}")
        
        print("Verifying...")
        is_match = verify_password(password, hashed)
        print(f"Match: {is_match}")
        
        if not is_match:
            print("ERROR: Password verification failed!")
    except Exception as e:
        print(f"BCRYPT ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bcrypt())
