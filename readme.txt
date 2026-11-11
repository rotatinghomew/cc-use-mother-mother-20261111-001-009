家庭医生签约资料同步机器人
社区工作人员校验家庭医生签约材料、居住地资格和家庭关系，再将可确认记录暂存到门户步骤并对账服务名册。

测试：python3 -m unittest discover -s tests/family_doctor_sync -p 'test_*.py'
构建：python3 -m compileall -q enrollment_sync tests/family_doctor_sync
验收：python3 -m enrollment_sync.desk.enrollment_cli --fixture fixtures/demo.json --database /tmp/family_doctor_sync-acceptance.sqlite3
