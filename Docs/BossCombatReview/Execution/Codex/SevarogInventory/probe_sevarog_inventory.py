"""C357 staged READ-ONLY synchronous inventory. No actor spawn, property set or asset save."""
import json
import unreal
ROOTS=('/Game/ParagonSevarog','/Game/OneBossFight/SevarogPack')
TARGETS=('/Game/OneBossFight/SevarogPack/BP_SevarogBossPack',
         '/Game/OneBossFight/SevarogPack/SevarogEnemyInfo',
         '/Game/OneBossFight/SevarogPack/SevarogCombatStyle')
unknown=[]
def emit(kind,value):
    unreal.log('[SEVAROG_INVENTORY]['+kind+'] '+json.dumps(value,sort_keys=True,ensure_ascii=True))
def plain(v):
    if v is None:return None
    if isinstance(v,(str,int,float,bool)):return v
    if hasattr(v,'get_path_name'):return v.get_path_name()
    try:return [plain(x) for x in v]
    except TypeError:return str(v)
def attempt(label,calls):
    failures=[]
    for api,call in calls:
        try:return {'status':'OBSERVED','api':api,'value':plain(call())}
        except Exception as ex:failures.append(api+': '+type(ex).__name__+': '+str(ex))
    unknown.append(label)
    return {'status':'UNKNOWN','label':label,'failures':failures}
def prop(obj,n):return obj.get_editor_property(n)
def rate(asset):
    candidates=[('get_sampling_frame_rate',lambda:asset.get_sampling_frame_rate()),
                ('sampling_frame_rate property',lambda:prop(asset,'sampling_frame_rate')),
                ('data_model.frame_rate',lambda:asset.get_data_model().get_frame_rate())]
    value=attempt(asset.get_path_name()+'.frame_rate',candidates)
    # Preserve numerator/denominator if exposed; never assume30fps or derive a rate from frame count/length.
    for api,call in candidates:
        try:
            f=call();value['numerator']=int(prop(f,'numerator'));value['denominator']=int(prop(f,'denominator'));break
        except Exception:pass
    return value
def notify_rows(asset):
    result=attempt(asset.get_path_name()+'.notifies',[
        ('AnimationLibrary.get_animation_notify_events',lambda:unreal.AnimationLibrary.get_animation_notify_events(asset)),
        ('notifies property',lambda:prop(asset,'notifies'))])
    # Fetch actual event objects separately; plain() output alone is not event-time authority.
    events=None
    try:events=unreal.AnimationLibrary.get_animation_notify_events(asset)
    except Exception:
        try:events=prop(asset,'notifies')
        except Exception:pass
    if events is None:return result
    rows=[]
    for i,event in enumerate(events):
        label=asset.get_path_name()+'.notify['+str(i)+']'
        rows.append({'name':attempt(label+'.name',[('notify_name property',lambda e=event:prop(e,'notify_name'))]),
                     'time_seconds':attempt(label+'.time',[
                         ('get_trigger_time',lambda e=event:e.get_trigger_time()),
                         ('get_time',lambda e=event:e.get_time()),
                         ('time property',lambda e=event:prop(e,'time')),
                         ('display_time property',lambda e=event:prop(e,'display_time'))]),
                     'duration':attempt(label+'.duration',[('duration property',lambda e=event:prop(e,'duration'))]),
                     'notify_object':attempt(label+'.object',[('notify property',lambda e=event:prop(e,'notify'))]),
                     'state_class':attempt(label+'.state',[('notify_state_class property',lambda e=event:prop(e,'notify_state_class'))])})
    return {'status':'OBSERVED','events':rows,'time_limit':'missing event-time APIs are UNKNOWN; trigger offsets are not substituted as absolute times'}
def curves(asset):
    rows={}
    for n in ('RCT_FLOAT','RCT_VECTOR','RCT_TRANSFORM'):
        rows[n]=attempt(asset.get_path_name()+'.curves.'+n,[('AnimationLibrary.get_animation_curve_names/'+n,
            lambda n=n:unreal.AnimationLibrary.get_animation_curve_names(asset,getattr(unreal.RawCurveTrackTypes,n)))])
    return rows
registry=unreal.AssetRegistryHelpers.get_asset_registry()
seen=set();records=[]
for root in ROOTS:
    data=registry.get_assets_by_path(root,recursive=True)
    emit('ROOT',{'root':root,'asset_data_count':len(data)})
    if not data:unknown.append(root+'.empty_or_unavailable_registry_root')
    for entry in sorted(data,key=lambda x:str(x.package_name)):
        class_name=str(entry.asset_class_path.asset_name)
        if class_name not in ('AnimSequence','AnimMontage'):continue
        package=str(entry.package_name)
        if package in seen:continue
        seen.add(package)
        obj=entry.get_asset()
        if obj is None:
            unknown.append(package+'.load_failed');emit('ANIMATION',{'path':package,'status':'LOAD_FAILED'});continue
        record={'name':obj.get_name(),'path':obj.get_path_name(),'class':class_name,
                'skeleton':attempt(package+'.skeleton',[('skeleton property',lambda:prop(obj,'skeleton'))]),
                'length_seconds':attempt(package+'.length',[('get_play_length',lambda:obj.get_play_length()),('sequence_length property',lambda:prop(obj,'sequence_length'))]),
                'frames':attempt(package+'.frames',[('AnimationLibrary.get_num_frames',lambda:unreal.AnimationLibrary.get_num_frames(obj))]),
                'frame_rate':rate(obj),
                'root_motion':attempt(package+'.root_motion',[('has_root_motion',lambda:obj.has_root_motion()),('enable_root_motion property',lambda:prop(obj,'enable_root_motion'))]),
                'notifies':notify_rows(obj),'curves':curves(obj)}
        emit('ANIMATION',record);records.append(package)
for package in TARGETS:
    obj=unreal.load_asset(package)
    row={'package':package,'asset':plain(obj),'dependencies':attempt(package+'.dependencies',[
        ('AssetRegistry.get_dependencies package+soft',lambda p=package:registry.get_dependencies(p,unreal.AssetRegistryDependencyOptions(include_soft_package_references=True,include_hard_package_references=True)))])}
    targets=[]
    if obj is not None:
        targets.append(('asset',obj))
        if obj.get_class().get_name()=='Blueprint':
            cls=unreal.load_class(None,package+'.'+package.rsplit('/',1)[-1]+'_C')
            if cls:targets.append(('class_default_object',unreal.get_default_object(cls)))
            else:unknown.append(package+'.generated_class_load')
    else:unknown.append(package+'.asset_load')
    row['properties']={}
    for kind,target in targets:
        names=[n for n in dir(target) if not n.startswith('_') and any(k in n.lower() for k in ('anim','montage','skeleton','enemy','style','ability','attack','behav','mesh'))]
        props={}
        for name in names:
            try:props[name]=plain(prop(target,name))
            except Exception:pass # methods are not properties; full candidate list retained below
        row['properties'][kind]={'candidate_names':names,'readable_properties':props,'limit':'filtered exposed properties + registry dependencies, NOT Blueprint graph logic'}
    emit('REFERENCE',row)
emit('SUMMARY',{'animation_count':len(records),'unique_animation_packages':records,'unknown_count':len(unknown),'unknown_fields':unknown,
    'status':'PARTIAL' if unknown else 'OBSERVED_INVENTORY','scope':'existing assets read only; no montage playback, timing tuning, graph execution, save or gameplay equivalence'})
