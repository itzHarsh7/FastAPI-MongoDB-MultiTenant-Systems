async def IsAdmin(request):
    role = request.state.role
    if role and role["name"] == "Admin":
        return True
    return False


async def IsTenant(request):
    role = request.state.role
    if role and role["name"] == "Tenant":
        return True
    return False


async def IsUser(request):
    role = request.state.role
    if role and role["name"] == "User":
        return True
    return False


async def IsAdminOrTenant(request):
    role = request.state.role
    if role and (role["name"] == "Admin" or role["name"] == "Tenant"):
        return True
    return False


async def AllowAny(request):
    return True


async def IsAuthenticated(request):
    user = request.state.user
    if user:
        return True
    return False
