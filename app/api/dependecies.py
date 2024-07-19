from typing import Annotated

from fastapi.params import Depends

from app.services.unitofwork import IUnitOfWork, UnitOfWork

UOWDep = Annotated[IUnitOfWork, Depends(UnitOfWork)]
