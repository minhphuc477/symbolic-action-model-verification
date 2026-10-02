@echo off
REM LOCM2 Real FSM Action Model Learner Execution Wrapper
pushd "%~dp0..\locm_repo"
python locm2.py %*
popd
