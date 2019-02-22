<!DOCTYPE html>
<html>
<head>  
    <title>${HTML_TITLE}</title>
    <link rel="shortcut icon" href="${STATIC_URL}images/bk_fta_solutions.png" type="image/x-icon">
    <link rel="stylesheet" href="${STATIC_URL}bootstrap/css/bootstrap.min.css?v=${STATIC_VERSION}"/>
    <link rel="stylesheet" type="text/css" href="${STATIC_URL}diy/css/index.css?v=${STATIC_VERSION}" />
    <script src="${STATIC_URL}js/jquery-1.10.2.min.js?v=${STATIC_VERSION}"></script>
    <link href="${STATIC_URL}css/bkDialog.css?v=${STATIC_VERSION}" rel="stylesheet">
    <script type="text/javascript" src="${SITE_URL}jsi18n/i18n/"></script>    

    <style>
        hr {
            margin: 10px;
        }

        .jtk-node {
            background-color: #3E7E9C;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            position: absolute;
            z-index: 11;
            overflow: hidden;
            min-width: 80px;
            min-height: 30px;
            width: auto;
        }

        .jtk-node .name {
            background-color: #3E7E9C;
            color: #f7ebca;
            cursor: move;
            font-size: 13px;
            line-height: 24px;
            padding: 6px;
            text-align: center;
        }

        .jtk-node .name span {
            cursor: pointer;
        }

        .connect1 {
            padding: 10px;
            background-color: #84ACB3;
        }

        .btn-add, .btn-del {
            width: 20px;
            height: 20px;
            position: absolute;
            cursor: pointer;
            top: 20px;
            line-height: 20px;
        }

        .btn-del {
            right: 15px;
        }

        .btn-add {
            left: 15px;
        }

        .jtk-node .bg_white{
            background: #3675C5;
        }
        .jtk-node  .bg_grey{
            background: grey;
        }
        .jtk-node.bg_white{
            background: #3675C5;
        }
        .jtk-node.bg_grey{
            background: grey;
        }
        .jtk-node .status_success{
            margin-right:6px;
            border:1px solid #69C2AF;
            color: #69C2AF;
        }
        .jtk-node .status_fail{
            margin-right:6px;
             border:1px solid red;
            color: red;
        }
        .node.success{
            background-color: #34a263;
        }
        .node.failure{
            background-color: #d9534f;
        }
        .node.running{
            background-color: #2180F5;
        }
        .node.noway{
            background-color: grey;
        }
        .node-text{
            color: white;
        }
        .bk-form-textarea::placeholder {
            color: #CCC;
        }
    </style>
</head>
<body>

<div style="padding:10px">
    <dl class='dl-horizontal'>
        <dt style='color:grey'>${_(u'告警详情')}</dt>
        <dd style='color:grey;width:80%'>
        ${_(u'业务')}
        <a href="${SITE_URL}${alarm.cc_biz_id}/?include=${alarm.cc_biz_id}/alarm_instance_list/" target="_blank">
        ${cc_biz_names.get(str(alarm.cc_biz_id), alarm.cc_biz_id)}
        </a>
        % if alarm.source_type == "LEAF":
            ${_(u'的告警对象')}: ${alarm.cc_topo_set if alarm.cc_topo_set else _(u"全业务")}
        % else:
            ${_(u'的主机')}
            ${alarm.ip}
        % endif
        ${_(u'在')}
            ${alarm.source_time_show}
        ${_(u'发生')}
        <a href="${SITE_URL}${alarm.cc_biz_id}/?include=${alarm.cc_biz_id}/alarm_def/${raw_alarm_def['id']}/" target="_blank">
        ${alarm_type_dict.get(alarm.alarm_type, alarm.alarm_type)}
        % if alarm.alarm_type in ['customized', 'leaf-biz-watchman']:
        (${raw_alarm_def['description']})
        % endif
        </a>
        : ${alarm.raw}
        </dd>
        <dt style='color:grey;padding-top:10px;'>${_(u'处理过程')}</dt>
        <dd id="log-content" style='color:grey;overflow-y:auto;max-height:200px;margin-top:10px;width:80%'>
            <%
            alarm_logs = alarm.alarm_log_list.filter(level__gte=20)
            %>
            %if len(alarm_logs) > 0:
                % for log in alarm_logs:
                    <div class="instance_log" data-step_name="${ log.step_name }">
                        <i class='bk-icon icon-check-circle'></i> ${ log.show_time } ${ ("#" + log.step_name.replace("graph_solution_", "")) if log.step_name and "graph_solution_" in log.step_name else "" } ${ log.content.replace("\n", "<br/>") |n}<br>
                    </div>
                %endfor
            %else:
                <div style="padding:0px 10px;">(${_(u'无')})</div>
            %endif
        </dd>
        <dt style='color:grey;padding-top:10px;'>${_(u'处理状态')}</dt>
        <dd style="padding-top:10px;">
                <span class="label label-${status_color_dict.get(alarm.status, 'default')}"  style='font-weight:normal'>
                % if alarm.status in ['recovering', 'converging', 'sleep', 'converged', 'retrying']:
                    <i class="bk-icon icon-refresh"></i>
                % endif
                    ${status_dict.get(alarm.status, '**unknown**')}
                </span>
                <span class="force-wrap" style='margin-left:10px;color:#7699B8'>
                % if alarm.comment:
                    ${alarm.comment |n}
                % else:
                    <a target="_blank" href="${SITE_URL}${alarm.cc_biz_id}/?include=${alarm.cc_biz_id}/solution/${solution.id}/">${solution.title_display}</a>
                % endif
                </span>
                % if alarm.status in ['recovering', 'converging', 'sleep', 'converged', 'retrying']:
                    <a href="javascript:;" class="selfFresh">${_(u'刷新页面')}</a>
                % endif
        </dd>
        %if alarm.status != "waiting":
        <dt style='color:grey;padding-top:15px;'>${_(u'操作')}</dt>
        <dd style="padding-top:10px;">
            % if alarm.status not in ['recovering', 'converging', 'sleep', 'converged', 'retrying']:
            <button class="btn btn-warning btn-sm" onclick="javascript:retry_flow(${alarm.id},0)">
                ${_(u'重试整个流程')}
            </button>
            % else:
            <button class="btn btn-danger btn-sm" onclick="javascript:stop_flow(${alarm.id})">
                ${_(u'终止处理流程')}
            </button>
            % endif
        </dd>
        % else:
        <dt style='color:grey;padding-top:10px;'>${_(u'审批')}</dt>
        <dd style="padding-top:10px;">

            <textarea class="bk-form-textarea" style="width: 500px;" placeholder="${_(u'审批意见')}" id="approve_text"></textarea>
                <div>
                    <button class="btn btn-success btn-sm" onclick="javascript:approve_flow(${alarm.id},true)">${_(u'通过')}</button>
                    <button class="btn btn-warning btn-sm" onclick="javascript:approve_flow(${alarm.id},false)">${_(u'拒绝')}</button>
                </div>

        </dd>
        %endif
    </dl>
</div>
<div class="widget-content" id="widget-content">
</div>

<div class="none node" id="node-templates">
    <div class="node-container">
        <i class="bk-icon icon-refresh btn-icon"></i>
        <div class="node-text"></div>
        <div class="option-group">
            <span class="option-btn success">${_(u'成功')}</span>
            <span class="option-btn failure">${_(u'失败')}</span>
            <span class="option-btn other">${_(u'其他')}</span>
        </div>
    </div>
</div>

<div style="width:100%">
    <div class="bktopo-container">
        <div id="bktopo"></div>
    </div>
</div>

<div class="resAlert rightD">
    <div class="resCenter"></div>
    <div class="btn-center">
          <a href="javascript:;" class="sureBtn">${_(u'确定')}</a>
    </div>
</div>

<script src="${STATIC_URL}diy/js/dagre.min.js?v=${STATIC_VERSION}"></script>
<script src="${STATIC_URL}diy/js/bkTopology.js?v=${STATIC_VERSION}"></script>
<script src="${STATIC_URL}bootstrap/js/bootstrap.min.js?v=${STATIC_VERSION}"></script>
<script src="${STATIC_URL}diy/js/alarm_instance_page.js?v=${STATIC_VERSION}"></script>
<script src="${STATIC_URL}js/bkDialog.js?v=${STATIC_VERSION}"></script>
<script>
<%
import json
%>
var solution_data = ${json.dumps(real_solutions)|n}
</script>
<script type="text/javascript">
    var site_url = "${SITE_URL}";           // app的url前缀,在ajax调用的时候，应该加上该前缀
    var alarm_cc_biz_id = "${alarm.cc_biz_id}";
    var alarm_id = "${alarm.id}"

    // 该页面进入之后每10s刷新一次
    setInterval(function(){
        window.location.reload()
    }, 10000)
</script>

<script src="${STATIC_URL}js/page_new/fta_solutions/alarm_instance_page.js"></script>

</body>
</html>
