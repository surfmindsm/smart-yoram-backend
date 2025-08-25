#!/usr/bin/env python3
"""
Manual verification of chat implementation changes
Checks the actual code changes without needing a running server
"""

import os
import sys
import re

def check_file_exists(filepath):
    """Check if file exists"""
    return os.path.exists(filepath)

def check_chat_request_schema():
    """Verify ChatRequest schema supports optional chat_history_id"""
    filepath = "app/schemas/ai_agent.py"
    
    print("🔍 Checking ChatRequest schema...")
    
    if not check_file_exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for optional chat_history_id
    if 'chat_history_id: Optional[Union[int, str]] = None' in content:
        print("✅ ChatRequest.chat_history_id is properly optional")
    else:
        print("❌ ChatRequest.chat_history_id is not optional")
        return False
    
    # Check for create_history_if_needed flag
    if 'create_history_if_needed: Optional[bool] = True' in content:
        print("✅ ChatRequest.create_history_if_needed is properly configured")
    else:
        print("❌ ChatRequest.create_history_if_needed flag is missing")
        return False
    
    return True

def check_chat_endpoint_logic():
    """Verify chat endpoint handles null chat_history_id"""
    filepath = "app/api/api_v1/endpoints/chat.py"
    
    print("\n🔍 Checking chat endpoint logic...")
    
    if not check_file_exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for auto-create logic
    auto_create_pattern = r'if chat_history_id is None and chat_request\.create_history_if_needed:'
    if re.search(auto_create_pattern, content):
        print("✅ Auto-create history logic is implemented")
    else:
        print("❌ Auto-create history logic is missing")
        return False
    
    # Check for new ChatHistory creation
    new_history_pattern = r'new_history = ChatHistory\('
    if re.search(new_history_pattern, content):
        print("✅ New ChatHistory creation logic is present")
    else:
        print("❌ New ChatHistory creation logic is missing")
        return False
    
    # Check for title generation from content
    title_pattern = r'title_preview = chat_request\.content\[:50\]'
    if re.search(title_pattern, content):
        print("✅ Automatic title generation is implemented")
    else:
        print("❌ Automatic title generation is missing")
        return False
    
    # Check for validation when auto-create is disabled
    validation_pattern = r'chat_history_id is required when create_history_if_needed is False'
    if re.search(validation_pattern, content):
        print("✅ Validation for disabled auto-create is implemented")
    else:
        print("❌ Validation for disabled auto-create is missing")
        return False
    
    return True

def check_default_agent_service():
    """Verify DefaultAgentService implementation"""
    filepath = "app/services/default_agent_service.py"
    
    print("\n🔍 Checking default agent service...")
    
    if not check_file_exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for default agent config
    if 'DEFAULT_AGENT_CONFIG' in content and '"id": 0' in content:
        print("✅ Default agent configuration is properly defined")
    else:
        print("❌ Default agent configuration is missing or incorrect")
        return False
    
    # Check for is_default_agent method
    if 'def is_default_agent(cls, agent_id: int)' in content:
        print("✅ is_default_agent method is implemented")
    else:
        print("❌ is_default_agent method is missing")
        return False
    
    # Check for get_agent_for_church method
    if 'def get_agent_for_church(' in content:
        print("✅ get_agent_for_church method is implemented")
    else:
        print("❌ get_agent_for_church method is missing")
        return False
    
    return True

def check_chat_endpoint_imports():
    """Verify chat endpoint has proper imports"""
    filepath = "app/api/api_v1/endpoints/chat.py"
    
    print("\n🔍 Checking chat endpoint imports...")
    
    if not check_file_exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for DefaultAgentService import
    if 'from app.services.default_agent_service import DefaultAgentService' in content:
        print("✅ DefaultAgentService is properly imported")
    else:
        print("❌ DefaultAgentService import is missing")
        return False
    
    return True

def check_agent_validation_logic():
    """Verify agent validation uses DefaultAgentService"""
    filepath = "app/api/api_v1/endpoints/chat.py"
    
    print("\n🔍 Checking agent validation logic...")
    
    if not check_file_exists(filepath):
        print(f"❌ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for agent validation using DefaultAgentService
    agent_validation_pattern = r'agent = DefaultAgentService\.get_agent_for_church\(agent_id, current_user\.church_id, db\)'
    if re.search(agent_validation_pattern, content):
        print("✅ Agent validation uses DefaultAgentService")
    else:
        print("❌ Agent validation does not use DefaultAgentService")
        return False
    
    return True

def main():
    """Run verification checks"""
    print("🔍 Manual Verification of Chat Implementation Changes")
    print("=" * 60)
    
    results = []
    
    # Check 1: ChatRequest schema
    results.append(check_chat_request_schema())
    
    # Check 2: Chat endpoint logic
    results.append(check_chat_endpoint_logic())
    
    # Check 3: Default agent service
    results.append(check_default_agent_service())
    
    # Check 4: Chat endpoint imports
    results.append(check_chat_endpoint_imports())
    
    # Check 5: Agent validation logic
    results.append(check_agent_validation_logic())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All implementation checks passed!")
        print("\n✅ Key features implemented:")
        print("  • ChatRequest supports optional chat_history_id")
        print("  • Auto-create history when chat_history_id is null")
        print("  • Automatic title generation from message content")
        print("  • Default agent service with ID: 0")
        print("  • Proper validation and error handling")
        return True
    else:
        print("❌ Some implementation issues detected.")
        return False

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    success = main()
    sys.exit(0 if success else 1)